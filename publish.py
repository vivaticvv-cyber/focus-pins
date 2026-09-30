"""FOCUS pins: планирование пинов на СЕГОДНЯ в Pinterest через Buffer (GraphQL API).

Запуск:
  python publish.py              обычный: запланировать в Buffer пины текущего дня (Киев)
  python publish.py --dry-run    ничего не отправлять и не менять, только показать, что было бы сделано
  python publish.py --check      проверка связи: токен, канал, доски, пауза очереди, очередь (только чтение)
  python publish.py --lint       проверка pins.csv (длины, хэштеги, картинки) без обращения к Buffer
  python publish.py --plan [N]   таблица «сколько пинов в день» на N дней вперёд (по умолчанию 45)

Документация Buffer: https://developers.buffer.com  (эндпоинт https://api.buffer.com, Authorization: Bearer <ключ>,
мутация createPost: schedulingType=automatic, mode=customScheduled, dueAt (UTC), assets[].image.url,
metadata.pinterest{title,url,boardServiceId}).
"""
import csv
import json
import os
import random
import sys
import time
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# =====================================================================
#                              КОНФИГ
# =====================================================================
CONFIG = dict(
    # --- Buffer / Pinterest ---
    CHANNEL_ID="6ab95df9ea19ca0bde06b951",          # канал Pinterest @Focus_adhd_planner
    ORG_ID="6ab95d486d34d034827f4193",
    BOARD_INFO="703617210473228341",                # ADHD Tips & Focus Hacks
    BOARD_PROMO="703617210473228343",               # FOCUS – ADHD Planner
    QUEUE_LIMIT=10,                                 # Buffer Free: до 10 запланированных постов на канал

    # --- сколько пинов в день ---
    START_DATE="2026-10-01",                        # день 1; до этой даты ничего не публикуется
    MAX_PER_DAY=10,                                 # жёсткий потолок (и запас под лимит очереди)
    STAGE_DAYS=10,                                  # длина этапа
    STAGE0_BASE=2, STAGE0_PLUS_DAYS=3,              # этап 1: базово 2, в 3 днях из 10 — по 3
    STAGE1_BASE=4, STAGE_STEP=2, PLUS_DAYS=3,       # этап 2: 4, дальше +2 за этап; в 3 днях из 10 — на 1 больше
    DOWN_DAYS=((1, 3), (2, 1)),                     # на максимуме: 3 дня на 1 меньше и 1 день на 2 меньше
    STOCK_DAYS=3,                                   # «склад» картинок на столько дней вперёд (generate.py)

    # --- время (Киев) ---
    WINDOW_START=(8, 0), WINDOW_END=(23, 30),
    MIN_GAP_MIN=40,                                 # минимальный интервал между пинами
    FALLBACK_GAP_MIN=25,                            # если 40 мин не помещается
    LEAD_MIN=20,                                    # при позднем запуске — не ближе чем через N минут от «сейчас»
    HOUR_WEIGHTS={8: 2, 9: 3, 10: 4, 11: 4, 12: 5, 13: 5, 14: 4, 15: 4, 16: 5, 17: 6,
                  18: 7, 19: 8, 20: 9, 21: 9, 22: 7, 23: 3},

    # --- доски ---
    PROMO_MIN_GAP=7,                                # между двумя промо-пинами минимум 7 обычных (~1 из 8)

    # --- ссылки: (url, вес) по типу доски. Итого ≈ 70% pages.dev / ≈ 23% dwshkr / ≈ 7% seqen ---
    LINKS={
        "info": [("https://focus-mini.pages.dev/", 74), ("https://vivatic.gumroad.com/l/dwshkr", 26)],
        "promo": [("https://focus-mini.pages.dev/", 45), ("https://vivatic.gumroad.com/l/seqen", 55)],
    },

    # --- проверка текста ---
    DESC_MIN=300, DESC_MAX=450, DESC_HARD_MAX=500,  # 500 — лимит Pinterest
    TITLE_MAX=100,
    HASHTAGS_MIN=3, HASHTAGS_MAX=4,
)

REPO = os.environ.get("GITHUB_REPOSITORY") or "vivaticvv-cyber/focus-pins"
BRANCH = os.environ.get("GITHUB_REF_NAME") or "main"
API_URL = "https://api.buffer.com"
FIELDS = ["id", "topic", "title", "pin_title", "description", "board", "status", "scene_prompt",
          "style", "layout", "link", "scheduled_at", "buffer_post_id"]


def cfg(name):
    """Значение конфига; START_DATE, MAX_PER_DAY, STOCK_DAYS можно переопределить переменной окружения."""
    if name in ("START_DATE", "MAX_PER_DAY", "STOCK_DAYS"):
        v = (os.environ.get(name) or "").strip()
        if v:
            return v if name == "START_DATE" else int(v)
    return CONFIG[name]


# =====================================================================
#                       ЧАСОВОЙ ПОЯС И ЧИСЛО ПИНОВ В ДЕНЬ
# =====================================================================
def kyiv():
    for name in ("Europe/Kyiv", "Europe/Kiev"):
        try:
            return ZoneInfo(name)
        except Exception:
            continue
    raise RuntimeError("нет часового пояса Europe/Kyiv (установите пакет tzdata)")


def now_kyiv():
    forced = (os.environ.get("FOCUS_NOW") or "").strip()      # только для тестов
    if forced:
        dt = datetime.fromisoformat(forced)
        return dt.astimezone(kyiv()) if dt.tzinfo else dt.replace(tzinfo=kyiv())
    return datetime.now(kyiv())


def start_date():
    return date.fromisoformat(str(cfg("START_DATE")))


def pins_for_day(day):
    """Детерминированно от даты: повторный запуск в тот же день даёт то же число."""
    k = (day - start_date()).days
    if k < 0:
        return 0
    sd = cfg("STAGE_DAYS")
    mx = cfg("MAX_PER_DAY")
    s, pos = divmod(k, sd)
    slots = list(range(sd))
    random.Random(f"focus-plan-{s}").shuffle(slots)
    if s == 0:
        base, ups = cfg("STAGE0_BASE"), cfg("STAGE0_PLUS_DAYS")
    else:
        base, ups = cfg("STAGE1_BASE") + cfg("STAGE_STEP") * (s - 1), cfg("PLUS_DAYS")
    if base >= mx:                                             # максимум: вариации вниз
        base, delta, i = mx, {}, 0
        for drop, cnt in cfg("DOWN_DAYS"):
            for _ in range(cnt):
                delta[slots[i]] = -drop
                i += 1
        val = base + delta.get(pos, 0)
    else:
        val = base + (1 if pos in set(slots[:ups]) else 0)
    return max(1, min(mx, val))


# =====================================================================
#                              ВРЕМЯ ПУБЛИКАЦИИ
# =====================================================================
def make_times(n, day, now, existing, rng):
    """n случайных времён на день `day` в окне 08:00–23:30 (Киев), веса по часам, интервал ≥ MIN_GAP,
    минуты не кратны 5. Если сегодня уже поздно — только оставшаяся часть окна.
    existing — уже занятые времена этого дня (учитываются при проверке интервала)."""
    tz = kyiv()
    ws = datetime.combine(day, dtime(*cfg("WINDOW_START")), tzinfo=tz)
    we = datetime.combine(day, dtime(*cfg("WINDOW_END")), tzinfo=tz)
    lo = ws
    if day == now.date():
        lo = max(ws, now + timedelta(minutes=cfg("LEAD_MIN")))
    if lo >= we or n <= 0:
        return []
    hours = sorted(cfg("HOUR_WEIGHTS"))
    weights = [cfg("HOUR_WEIGHTS")[h] for h in hours]

    def attempt(k, gap):
        chosen = []
        for _ in range(k):
            for _try in range(300):
                h = rng.choices(hours, weights)[0]
                m = rng.randrange(60)
                if m % 5 == 0:
                    continue
                t = datetime.combine(day, dtime(h, m), tzinfo=tz)
                if t < lo or t > we:
                    continue
                if any(abs(t - x) < gap for x in chosen + list(existing)):
                    continue
                chosen.append(t)
                break
            else:
                return None
        return sorted(chosen)

    for k in range(n, 0, -1):
        for gap_min in (cfg("MIN_GAP_MIN"), cfg("FALLBACK_GAP_MIN")):
            for _ in range(40):
                res = attempt(k, timedelta(minutes=gap_min))
                if res:
                    return res
    return []


def to_utc_z(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


# =====================================================================
#                                CSV
# =====================================================================
def load_rows(path="pins.csv"):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        rows = [dict(r) for r in rd]
        header = list(rd.fieldnames or [])
    return rows, header


def save_rows(rows, header, path="pins.csv"):
    fields = list(header) + [c for c in FIELDS if c not in header]
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def status(r):
    return (r.get("status") or "").strip().lower()


def parse_dt(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt.astimezone(kyiv()) if dt.tzinfo else dt.replace(tzinfo=kyiv())


def board_kind(name):
    n = (name or "").lower()
    return "promo" if ("planner" in n and "tips" not in n) else "info"


def choose_link(row):
    """Ссылка, заданная в CSV, сохраняется; иначе — взвешенный выбор, стабильный для конкретного id."""
    ready = (row.get("link") or "").strip()
    if ready:
        return ready
    opts = cfg("LINKS")[board_kind(row.get("board"))]
    urls, ws = [u for u, _ in opts], [w for _, w in opts]
    return random.Random(f"focus-link-{row.get('id')}").choices(urls, ws)[0]


def choose_pins(cands, since_promo, k):
    """k пинов из готовых (по возрастанию id); промо — не чаще одного на PROMO_MIN_GAP обычных, не подряд."""
    pool, picks = list(cands), []
    while len(picks) < k:
        pick = None
        for r in pool:
            if board_kind(r.get("board")) == "promo":
                if since_promo >= cfg("PROMO_MIN_GAP"):
                    pick = r
                    break
            else:
                pick = r
                break
        if pick is None:
            break
        pool.remove(pick)
        picks.append(pick)
        since_promo = 0 if board_kind(pick.get("board")) == "promo" else since_promo + 1
    return picks


def since_last_promo(rows):
    hist = [r for r in rows if status(r) in ("scheduled", "published")]
    hist.sort(key=lambda r: (parse_dt(r.get("scheduled_at")) or datetime.min.replace(tzinfo=timezone.utc),
                             int(r["id"])))
    n = 0
    for r in reversed(hist):
        if board_kind(r.get("board")) == "promo":
            return n
        n += 1
    return n


def clip_title(t, limit):
    t = (t or "").strip()
    if len(t) <= limit:
        return t
    return t[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-—")


def validate_row(r, images_dir="images"):
    """Ошибки, из-за которых пин отправлять нельзя."""
    errs = []
    desc = (r.get("description") or "").strip()
    if not desc:
        errs.append("пустое описание")
    if len(desc) > cfg("DESC_HARD_MAX"):
        errs.append(f"описание {len(desc)} симв. > {cfg('DESC_HARD_MAX')} (лимит Pinterest)")
    if not ((r.get("pin_title") or r.get("title") or "").strip()):
        errs.append("нет pin_title/title")
    if not Path(images_dir, f"{r['id']}.jpg").exists():
        errs.append(f"нет файла {images_dir}/{r['id']}.jpg")
    return errs


# =====================================================================
#                               BUFFER
# =====================================================================
class BufferError(RuntimeError):
    """Ошибка Buffer, после которой нужно остановиться."""


class BufferAuthError(BufferError):
    pass


class BufferClient:
    def __init__(self, token):
        self.token = token

    def graphql(self, query, variables=None, mutation=False):
        payload = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        last = None
        for attempt in range(4):
            try:
                r = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            except requests.RequestException as e:
                last = e
                if mutation:      # запрос мог дойти — повтор создал бы дубль; следующий запуск подхватит пост сам
                    raise BufferError(f"сетевая ошибка при создании поста: {e}")
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code in (401, 403):
                raise BufferAuthError(f"HTTP {r.status_code}: ключ Buffer недействителен или нет прав")
            if r.status_code == 429 or (r.status_code >= 500 and not mutation):
                last = f"HTTP {r.status_code}"
                time.sleep(min(int(r.headers.get("Retry-After", 0) or 0) or 15 * (2 ** attempt), 120))
                continue
            try:
                j = r.json()
            except ValueError:
                raise BufferError(f"Buffer вернул не JSON (HTTP {r.status_code}): {r.text[:200]}")
            errs = j.get("errors")
            if errs:
                code = ((errs[0].get("extensions") or {}).get("code")) or ""
                msg = errs[0].get("message", "")
                if code in ("UNAUTHORIZED", "FORBIDDEN"):
                    raise BufferAuthError(f"{code}: {msg}")
                if code == "RATE_LIMIT_EXCEEDED" and attempt < 3:
                    last = code
                    time.sleep(15 * (2 ** attempt))
                    continue
                if code == "UNEXPECTED" and not mutation and attempt < 3:
                    last = code
                    time.sleep(5 * (attempt + 1))
                    continue
                raise BufferError(f"{code or 'ошибка'}: {msg}")
            return j.get("data") or {}
        raise BufferError(f"Buffer недоступен: {last}")


CREATE_POST = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id dueAt status } }
    ... on MutationError { message }
  }
}
"""


def create_pin(client, *, text, title, link, board_id, image_url, due_utc):
    inp = {
        "channelId": cfg("CHANNEL_ID"),
        "text": text,
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_utc,
        "assets": [{"image": {"url": image_url}}],
        "metadata": {"pinterest": {"title": title, "url": link, "boardServiceId": board_id}},
    }
    data = client.graphql(CREATE_POST, {"input": inp}, mutation=True)
    res = data.get("createPost") or {}
    post = res.get("post")
    if post and post.get("id"):
        return post["id"], post.get("dueAt")
    raise BufferError(f"{res.get('__typename', 'MutationError')}: {res.get('message', 'неизвестная ошибка')}")


def fetch_scheduled(client):
    """Запланированные посты канала: [{id,text,dueAt}]. Нужны для лимита очереди и подхвата «потерянных» постов."""
    q = ("query { posts(first: 50, input: {organizationId: %s, sort: [{field: dueAt, direction: asc}], "
         "filter: {status: [scheduled], channelIds: [%s]}}) { edges { node { id text dueAt } } } }"
         % (json.dumps(cfg("ORG_ID")), json.dumps(cfg("CHANNEL_ID"))))
    data = client.graphql(q)
    return [e["node"] for e in ((data.get("posts") or {}).get("edges") or [])]


def check_connection(client):
    q = ("query { channel(input: {id: %s}) { id name service isDisconnected isQueuePaused "
         "metadata { ... on PinterestMetadata { boards { name serviceId } } } } }" % json.dumps(cfg("CHANNEL_ID")))
    ch = client.graphql(q).get("channel")
    if not ch:
        raise BufferError("канал не найден (проверьте CHANNEL_ID)")
    boards = ((ch.get("metadata") or {}).get("boards")) or []
    print(f"Канал: {ch.get('name')} [{ch.get('service')}]  отключён: {ch.get('isDisconnected')}  "
          f"очередь на паузе: {ch.get('isQueuePaused')}")
    for b in boards:
        print(f"  доска: {b.get('name')} -> {b.get('serviceId')}")
    ok = True
    if ch.get("isDisconnected"):
        print("::error::Канал Pinterest отключён в Buffer — переподключите его")
        ok = False
    if ch.get("isQueuePaused"):
        print("::error::Очередь канала на паузе — посты не будут публиковаться")
        ok = False
    ids = {b.get("serviceId") for b in boards}
    for name in ("BOARD_INFO", "BOARD_PROMO"):
        if ids and cfg(name) not in ids:
            print(f"::error::{name}={cfg(name)} нет среди досок канала")
            ok = False
    return ok


# =====================================================================
#                          ОСНОВНОЙ ЗАПУСК
# =====================================================================
def image_url(rid):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/images/{rid}.jpg"


def url_reachable(url):
    """Buffer скачивает картинку сам: убеждаемся, что она уже видна публично (кэш raw бывает с задержкой)."""
    for i in range(3):
        try:
            r = requests.head(url, timeout=20, allow_redirects=True)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
                return True
        except requests.RequestException:
            pass
        time.sleep(5 * (i + 1))
    return False


def mark_published(rows, now):
    n = 0
    for r in rows:
        if status(r) == "scheduled":
            dt = parse_dt(r.get("scheduled_at"))
            if dt and dt < now - timedelta(minutes=15):
                r["status"] = "published"
                n += 1
    return n


def run(mode="run", now=None, client=None, csv_path="pins.csv", images_dir="images", rng=None, url_ok=None):
    """Возвращает код выхода: 0 — всё хорошо, 1 — были ошибки (прогон должен стать красным)."""
    dry = mode == "dry-run"
    now = now or now_kyiv()
    rng = rng or random.Random()
    url_ok = url_ok or url_reachable
    rows, header = load_rows(csv_path)
    red = False

    if mark_published(rows, now) and not dry:
        save_rows(rows, header, csv_path)

    today = now.date()
    plan = pins_for_day(today)
    print(f"Сегодня {today} (Киев), день №{(today - start_date()).days + 1}, по плану пинов: {plan}")
    if plan == 0:
        print("До START_DATE — публикация не начата.")
        return 0

    # --- что уже стоит в Buffer (лимит очереди + подхват постов, чей id не успел записаться в CSV) ---
    remote = None
    if client is not None:
        try:
            remote = fetch_scheduled(client)
        except BufferAuthError:
            raise
        except BufferError as e:
            print(f"::warning::Не удалось прочитать очередь Buffer ({e}); продолжаю без сверки")
    if remote:
        by_text = {(p.get("text") or "").strip(): p for p in remote}
        for r in rows:
            if status(r) == "ready" and (r.get("description") or "").strip() in by_text:
                p = by_text[(r.get("description") or "").strip()]
                r["status"] = "scheduled"
                r["buffer_post_id"] = p["id"]
                due = parse_dt(p.get("dueAt"))
                r["scheduled_at"] = due.isoformat(timespec="minutes") if due else ""
                print(f"Подхвачен уже запланированный пин {r['id']} (id поста {p['id']})")
        if not dry:
            save_rows(rows, header, csv_path)

    assigned = []
    for r in rows:
        if status(r) in ("scheduled", "published"):
            dt = parse_dt(r.get("scheduled_at"))
            if dt and dt.date() == today:
                assigned.append(dt)
    need = plan - len(assigned)
    if need <= 0:
        print(f"На сегодня уже всё запланировано ({len(assigned)}/{plan}).")
        return 0

    times = make_times(need, today, now, assigned, rng)
    if not times:
        print("::warning::В оставшейся части окна публикации нет места — на сегодня пинов больше не будет.")
        return 0
    if len(times) < need:
        print(f"::warning::Нужно {need}, но в оставшееся время помещается {len(times)}.")

    queued = len(remote) if remote is not None else 0
    room = cfg("QUEUE_LIMIT") - queued
    if room < len(times):
        print(f"::error::Очередь Buffer: уже {queued} из {cfg('QUEUE_LIMIT')}, можно добавить только {max(room, 0)}")
        times = times[:max(room, 0)]
        red = True

    cands = sorted((r for r in rows if status(r) == "ready"), key=lambda r: int(r["id"]))
    picks = choose_pins(cands, since_last_promo(rows), len(times))
    if len(picks) < len(times):
        print(f"::warning::Готовых пинов не хватает: нужно {len(times)}, подходящих {len(picks)} "
              f"(промо не ставится раньше чем через {cfg('PROMO_MIN_GAP')} обычных)")
        times = times[:len(picks)]
    if not picks:
        print("::error::Нет подходящих готовых пинов (status=ready) — пополните pins.csv / дождитесь generate.py")
        return 1

    scheduled = 0
    for r, when in zip(picks, times):
        errs = validate_row(r, images_dir)
        if errs:
            print(f"::error::Пин {r['id']} пропущен: {'; '.join(errs)}")
            red = True
            continue
        kind = board_kind(r.get("board"))
        board_id = cfg("BOARD_PROMO") if kind == "promo" else cfg("BOARD_INFO")
        link = choose_link(r)
        title = clip_title(r.get("pin_title") or r.get("title"), cfg("TITLE_MAX"))
        url = image_url(r["id"])
        line = f"пин {r['id']:>3} [{kind}] {when:%H:%M} -> {link}"
        if dry:
            print("DRY  " + line)
            continue
        if not url_ok(url):
            print(f"::error::Пин {r['id']}: картинка недоступна по {url} (закоммичена ли она?)")
            red = True
            continue
        try:
            post_id, due = create_pin(client, text=r["description"].strip(), title=title, link=link,
                                      board_id=board_id, image_url=url, due_utc=to_utc_z(when))
        except BufferError as e:
            print(f"::error::Buffer: {e}. Останавливаюсь; уже запланированное сохранено.")
            save_rows(rows, header, csv_path)
            return 1
        r["status"] = "scheduled"
        r["scheduled_at"] = when.isoformat(timespec="minutes")
        r["link"] = link
        r["buffer_post_id"] = post_id
        save_rows(rows, header, csv_path)      # сразу после каждого успеха — чтобы не потерять при сбое
        scheduled += 1
        print("OK   " + line + f"  (post {post_id})")

    print(("Проверка без отправки завершена." if dry else f"Готово: запланировано {scheduled} из {plan} на сегодня."))
    return 1 if red else 0


# =====================================================================
#                          LINT и PLAN
# =====================================================================
def lint(csv_path="pins.csv", images_dir="images"):
    rows, _ = load_rows(csv_path)
    bad = 0
    seen_desc, seen_title = {}, {}
    for r in rows:
        rid, msgs = r["id"], []
        d = (r.get("description") or "").strip()
        tags = [w for w in d.split() if w.startswith("#")]
        if not (cfg("DESC_MIN") <= len(d) <= cfg("DESC_MAX")):
            msgs.append(f"описание {len(d)} симв. (нужно {cfg('DESC_MIN')}–{cfg('DESC_MAX')})")
        if not (cfg("HASHTAGS_MIN") <= len(tags) <= cfg("HASHTAGS_MAX")):
            msgs.append(f"хэштегов {len(tags)} (нужно {cfg('HASHTAGS_MIN')}–{cfg('HASHTAGS_MAX')})")
        pt = (r.get("pin_title") or "").strip()
        if not pt:
            msgs.append("нет pin_title")
        elif len(pt) > cfg("TITLE_MAX"):
            msgs.append(f"pin_title {len(pt)} симв. > {cfg('TITLE_MAX')}")
        t = (r.get("title") or "").strip().lower().rstrip("?.!")
        if t and t in d.lower():
            msgs.append("описание повторяет надпись на картинке (title)")
        if d in seen_desc:
            msgs.append(f"описание совпадает с пином {seen_desc[d]}")
        seen_desc.setdefault(d, rid)
        if (r.get("board") or "").strip() == "":
            msgs.append("не указана доска")
        scene = (r.get("scene_prompt") or "").lower()
        bad_words = [w for w in ("laptop", "screen", "phone", "computer", "hand ", "hands", "person", "people",
                                 "man ", "woman", "girl", "boy ", "human", "face") if w in scene + " "]
        if bad_words:
            msgs.append("в сцене нежелательные слова: " + ", ".join(w.strip() for w in bad_words)
                        + " (используйте {mascot} или предмет-метафору)")
        if status(r) in ("ready", "scheduled", "published") and not Path(images_dir, f"{rid}.jpg").exists() \
                and status(r) == "ready":
            msgs.append(f"status=ready, но нет {images_dir}/{rid}.jpg")
        if msgs:
            bad += 1
            print(f"пин {rid}: " + "; ".join(msgs))
    promo = sum(1 for r in rows if board_kind(r.get("board")) == "promo")
    print(f"Строк: {len(rows)}, промо: {promo} ({100 * promo // max(len(rows), 1)}%), с замечаниями: {bad}")
    return 1 if bad else 0


def print_plan(days=45):
    d0 = start_date()
    total = 0
    print("день  дата        пинов")
    for i in range(days):
        d = d0 + timedelta(days=i)
        n = pins_for_day(d)
        total += n
        print(f"{i + 1:>3}   {d}   {n:>2}  {'#' * n}")
    print(f"Всего за {days} дн.: {total}")


def main(argv):
    if "--plan" in argv:
        i = argv.index("--plan")
        print_plan(int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 45)
        return 0
    if "--lint" in argv:
        return lint()
    token = (os.environ.get("BUFFER_TOKEN") or "").strip()
    client = BufferClient(token) if token else None
    try:
        if "--check" in argv:
            if not client:
                print("::error::BUFFER_TOKEN не задан")
                return 1
            ok = check_connection(client)
            queued = fetch_scheduled(client)
            print(f"В очереди Buffer сейчас: {len(queued)} из {cfg('QUEUE_LIMIT')}")
            return 0 if ok else 1
        if "--dry-run" in argv:
            return run("dry-run", client=client)
        if not client:
            print("::error::BUFFER_TOKEN не задан")
            return 1
        return run("run", client=client)
    except BufferAuthError as e:
        print(f"::error::Buffer отклонил ключ: {e}. Проверьте секрет BUFFER_TOKEN.")
        return 1
    except BufferError as e:
        print(f"::error::Buffer: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
