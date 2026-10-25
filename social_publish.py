"""FOCUS social: планирование постов Facebook и X в Buffer (по social.csv).

Запуск:
  python social_publish.py              обычный: запланировать в Buffer посты текущего дня (Киев)
  python social_publish.py --dry-run    только показать, что было бы сделано
  python social_publish.py --check      проверка связи: токен, каналы, пауза очереди, очереди (только чтение)
  python social_publish.py --lint       проверка готовых строк social.csv без обращения к Buffer
  python social_publish.py --plan [N]   план по дням и примерное время публикации на N дней (по умолчанию 30)

Дополняет Metricool (Facebook) и Typefully (X), а не заменяет их: их запланированные посты перечислены в
external_posts.csv (network, datetime, source). В дни, где у сети уже есть такой пост, Buffer не публикует.
Файл надо обновлять по живому расписанию Metricool/Typefully (раз в неделю).

Время: окна заданы в поясе США (America/New_York) — переход на зимнее время в США (1 нояб.) и в Европе (25 окт.)
учитывается сам. Минуты случайные (не кратны 5), час не повторяет часы предыдущих постов этой сети, поэтому
расписание выглядит как у человека. Для одного дня время детерминированно (план и боевой запуск совпадают).

Правила: Facebook — ссылки в теле поста нет, ссылка только в первом комментарии (колонка first_comment, токен {link});
X — ссылка в тексте не чаще чем в 1 из LINK_GAP_X постов; ссылки и код BF30 строит social.build_link.
Картинки: колонка image (images/social/...), строки со status=ready.
"""
import csv
import json
import os
import random
import sys
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import publish as P
import social as S

CONFIG = dict(
    ORG_ID=P.CONFIG["ORG_ID"],
    CHANNELS={"facebook": "6ac9c9376a5c39ccb66d4b86", "x": "6ac9c83c6a5c39ccb66d328e"},
    QUEUE_LIMIT=10,
    # Начало публикации через Buffer; можно переопределить переменными репозитория FB_START / X_START.
    START={"facebook": "2026-10-16", "x": "2026-10-16"},
    # (период в днях, номера дней периода, в которые публикуем)
    PATTERN={"facebook": (3, (0,)), "x": (1, (0,))},   # Facebook: Buffer каждый 3-й день (остальные дни — Metricool); X: каждый день, кроме дней Typefully (SKIP_BUSY_DAYS по external_posts.csv)
    # Часы публикации по времени США (Восток) -> вес. Будни: утро и обед/после обеда; выходные — только середина дня.
    HOURS_ET={
        "facebook": {8: 3, 9: 5, 10: 5, 11: 3, 12: 6, 13: 5, 14: 5, 15: 3, 16: 1},
        "x": {8: 3, 9: 4, 10: 3, 11: 4, 12: 6, 13: 6, 14: 5, 15: 3},
    },
    WEEKEND_HOURS_ET=(10, 11, 12, 13, 14),
    MIN_GAP_MIN=120,
    LEAD_MIN=20,
    RECENT_HOURS_N=3,        # час (ET) не повторяет часы трёх последних постов этой сети
    LINK_GAP_X=6,            # ссылка в тексте X не чаще чем раз в 7 постов
    SHOWCASE_GAP=3,          # витринные посты не чаще 1 из 4 в каждой сети
    X_LIMIT=280, X_LINK_LEN=23,
    FB_TEXT_MIN=180, FB_TEXT_MAX=700,
    HASHTAGS_MAX=2,
    SKIP_BUSY_DAYS=True,     # в дни, когда у сети уже есть пост Metricool/Typefully, Buffer не публикует
)
CSV = "social.csv"
EXTERNAL = "external_posts.csv"
ET = ZoneInfo("America/New_York")


def cfg(name):
    return CONFIG[name]


# ------------------------------------------------------------------ CSV
def load(path=CSV):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        rows = [dict(r) for r in rd]
        header = list(rd.fieldnames or [])
    return rows, header


def save(rows, header, path=CSV):
    fields = list(header) + [c for c in S.FIELDS if c not in header]
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def load_external(path=None):
    """{сеть: [datetime (Киев)]} запланированных внешних постов (Metricool/Typefully). Нет файла — пусто."""
    path = path or os.environ.get("EXTERNAL_CSV") or EXTERNAL
    ext = {n: [] for n in cfg("CHANNELS")}
    if not Path(path).exists():
        return ext
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            dt = P.parse_dt(r.get("datetime"))
            if dt and r.get("network") in ext:
                ext[r["network"]].append(dt)
    return ext


# ------------------------------------------------------------------ план по дням и время
def net_start(net):
    v = (os.environ.get("FB_START" if net == "facebook" else "X_START") or "").strip()
    return date.fromisoformat(v or cfg("START")[net])


def posts_for_day(net, day, external=None):
    k = (day - net_start(net)).days
    if k < 0:
        return 0
    period, slots = cfg("PATTERN")[net]
    if (k % period) not in slots:
        return 0
    if cfg("SKIP_BUSY_DAYS") and external and any(d.date() == day for d in external.get(net, ())):
        return 0
    return 1


def recent_hours(net, rows, external, before):
    """Часы (ET) последних постов сети — чтобы не повторять один и тот же час."""
    times = [P.parse_dt(r.get("scheduled_at")) for r in rows
             if r.get("network") == net and P.status(r) in ("scheduled", "published")]
    times += external.get(net, [])
    times = sorted(t for t in times if t and t < before)
    return {t.astimezone(ET).hour for t in times[-cfg("RECENT_HOURS_N"):]}


def make_time(net, day, now, taken, rng, avoid_hours=()):
    """Время поста для дня `day` (по Киеву) в окне по США; None, если не поместилось."""
    kyiv = P.kyiv()
    hours = dict(cfg("HOURS_ET")[net])
    if datetime.combine(day, dtime(12), tzinfo=kyiv).astimezone(ET).weekday() >= 5:
        hours = {h: w for h, w in hours.items() if h in cfg("WEEKEND_HOURS_ET")}
    preferred = {h: w for h, w in hours.items() if h not in avoid_hours} or hours
    lo = now + timedelta(minutes=cfg("LEAD_MIN")) if day == now.date() else None
    gap = timedelta(minutes=cfg("MIN_GAP_MIN"))
    for pool in (preferred, hours):
        hs = sorted(pool)
        ws = [pool[h] for h in hs]
        for _ in range(500):
            h = rng.choices(hs, ws)[0]
            m = rng.randrange(60)
            if m % 5 == 0:
                continue
            et_day = datetime.combine(day, dtime(12), tzinfo=kyiv).astimezone(ET).date()
            t = datetime.combine(et_day, dtime(h, m), tzinfo=ET).astimezone(kyiv)
            if t.date() != day or (lo and t < lo) or any(abs(t - x) < gap for x in taken):
                continue
            return t
    return None


# ------------------------------------------------------------------ выбор и сборка поста
def status(r):
    return P.status(r)


def _hist(rows, net):
    h = [r for r in rows if r["network"] == net and status(r) in ("scheduled", "published")]
    h.sort(key=lambda r: (P.parse_dt(r.get("scheduled_at")) or datetime.min.replace(tzinfo=timezone.utc), r["id"]))
    return h


def since_kind(rows, net, kind):
    n = 0
    for r in reversed(_hist(rows, net)):
        if r.get("kind") == kind:
            return n
        n += 1
    return n


def since_x_link(rows):
    n = 0
    for r in reversed(_hist(rows, "x")):
        if (r.get("link_key") or "").strip():
            return n
        n += 1
    return n


def choose(rows, net):
    """Обычные посты идут по возрастанию id; витринные (showcase) вставляются не чаще 1 из SHOWCASE_GAP+1."""
    cands = sorted((r for r in rows if r["network"] == net and status(r) == "ready"
                    and not r["id"].startswith("M")), key=lambda r: r["id"])      # M-строки — для Metricool
    xl = since_x_link(rows) if net == "x" else 0

    def link_ok(r):
        return not (net == "x" and (r.get("link_key") or "").strip() and xl < cfg("LINK_GAP_X"))

    show = [r for r in cands if r.get("kind") == "showcase" and link_ok(r)]
    if show and since_kind(rows, net, "showcase") >= cfg("SHOWCASE_GAP"):
        return show[0]
    for r in cands:
        if r.get("kind") != "showcase" and link_ok(r):
            return r
    return show[0] if show else None


def compose_text(r, when):
    """(текст поста, первый комментарий или '')."""
    net = r["network"]
    text = (r.get("text") or "").strip()
    fc = (r.get("first_comment") or "").strip()
    key = (r.get("link_key") or "").strip()
    link = S.build_link(key, net, r["id"], r.get("kind") or "post", when) if key else ""
    if net == "facebook":
        return text, (fc.replace("{link}", link) if fc else "")
    return (f"{text} {link}".strip() if link else text), ""


def x_length(text):
    """X считает любую ссылку как 23 символа."""
    words = text.split(" ")
    return sum(cfg("X_LINK_LEN") if w.startswith("http") else len(w) for w in words) + max(len(words) - 1, 0)


def validate(r, root=".", when=None):
    errs = []
    net = r["network"]
    if net not in cfg("CHANNELS"):
        return [f"неизвестная сеть {net!r}"]
    text, fc = compose_text(r, when or P.now_kyiv())
    if not text:
        errs.append("пустой текст")
    if net == "x" and x_length(text) > cfg("X_LIMIT"):
        errs.append(f"текст X {x_length(text)} симв. > {cfg('X_LIMIT')}")
    if net == "facebook":
        if not cfg("FB_TEXT_MIN") <= len(text) <= cfg("FB_TEXT_MAX"):
            errs.append(f"текст Facebook {len(text)} симв. (нужно {cfg('FB_TEXT_MIN')}–{cfg('FB_TEXT_MAX')})")
        if "http" in text:
            errs.append("ссылка в теле поста Facebook (она должна быть только в первом комментарии)")
    tags = [w for w in (r.get("text") or "").split() if w.startswith("#")]
    if len(tags) > cfg("HASHTAGS_MAX"):
        errs.append(f"хэштегов {len(tags)} (нужно не больше {cfg('HASHTAGS_MAX')})")
    key = (r.get("link_key") or "").strip()
    if key and key not in S.LINKS:
        errs.append(f"неизвестный link_key {key!r}")
    if "{link}" in (r.get("first_comment") or "") and not key:
        errs.append("в first_comment есть {link}, но link_key пуст")
    img = (r.get("image") or "").strip()
    if not img:
        errs.append("не указана картинка")
    elif not Path(root, img).exists():
        errs.append(f"нет файла {img}")
    return errs


# ------------------------------------------------------------------ Buffer
def image_url(rel):
    return f"https://raw.githubusercontent.com/{P.REPO}/{P.BRANCH}/{rel}"


def create_social(client, *, net, text, first_comment, image_rel, due_utc, use_first_comment=True):
    """Создаёт пост в Buffer. Для Facebook first_comment — платная фича; при Free-плане
    выставляем use_first_comment=False и ссылку не кладём в комментарий."""
    inp = {
        "channelId": cfg("CHANNELS")[net],
        "text": text,
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_utc,
        "assets": [{"image": {"url": image_url(image_rel)}}],
    }
    if net == "facebook":
        meta = {"type": "post"}
        if first_comment and use_first_comment:
            meta["firstComment"] = first_comment
        inp["metadata"] = {"facebook": meta}
    data = client.graphql(P.CREATE_POST, {"input": inp}, mutation=True)
    res = data.get("createPost") or {}
    post = res.get("post")
    if post and post.get("id"):
        return post["id"], post.get("dueAt")
    raise P.BufferError(f"{res.get('__typename', 'MutationError')}: {res.get('message', 'неизвестная ошибка')}")


def fetch_scheduled(client, channel_id):
    q = ("query { posts(first: 50, input: {organizationId: %s, sort: [{field: dueAt, direction: asc}], "
         "filter: {status: [scheduled], channelIds: [%s]}}) { edges { node { id text dueAt } } } }"
         % (json.dumps(cfg("ORG_ID")), json.dumps(channel_id)))
    data = client.graphql(q)
    return [e["node"] for e in ((data.get("posts") or {}).get("edges") or [])]


def check_connection(client):
    ok = True
    for net, cid in cfg("CHANNELS").items():
        q = ("query { channel(input: {id: %s}) { id name service isDisconnected isQueuePaused } }"
             % json.dumps(cid))
        ch = client.graphql(q).get("channel")
        if not ch:
            print(f"::error::канал {net} не найден (проверьте id {cid})")
            ok = False
            continue
        print(f"{net}: {ch.get('name')} [{ch.get('service')}]  отключён: {ch.get('isDisconnected')}  "
              f"очередь на паузе: {ch.get('isQueuePaused')}")
        if ch.get("isDisconnected"):
            print(f"::error::Канал {net} отключён в Buffer — переподключите")
            ok = False
        if ch.get("isQueuePaused"):
            print(f"::error::Очередь канала {net} на паузе")
            ok = False
        print(f"  в очереди: {len(fetch_scheduled(client, cid))} из {cfg('QUEUE_LIMIT')}")
    return ok


# ------------------------------------------------------------------ основной запуск
def run(mode="run", now=None, client=None, csv_path=CSV, root=".", rng=None, url_ok=None):
    dry = mode == "dry-run"
    now = now or P.now_kyiv()
    url_ok = url_ok or P.url_reachable
    rows, header = load(csv_path)
    external = load_external()
    red = False
    today = now.date()

    if P.mark_published(rows, now) and not dry:
        save(rows, header, csv_path)

    for net in cfg("CHANNELS"):
        plan = posts_for_day(net, today, external)
        why = ""
        if plan == 0:
            busy = any(d.date() == today for d in external.get(net, ()))
            why = " (в этот день уже есть пост Metricool/Typefully)" if busy else \
                  f" (старт {net_start(net)}, день вне шаблона)"
        print(f"[{net}] {today}: по плану постов {plan}{why}")
        if plan == 0:
            continue
        remote = None
        if client is not None:
            try:
                remote = fetch_scheduled(client, cfg("CHANNELS")[net])
            except P.BufferAuthError:
                raise
            except P.BufferError as e:
                print(f"::warning::[{net}] не удалось прочитать очередь Buffer ({e}); продолжаю без сверки")
        if remote:
            by_text = {(p.get("text") or "").strip(): p for p in remote}
            for r in rows:
                if r["network"] != net or status(r) != "ready":
                    continue
                t = (r.get("text") or "").strip()
                hit = next((p for tx, p in by_text.items() if tx == t or tx.startswith(t + " http")), None)
                if hit:
                    due = P.parse_dt(hit.get("dueAt"))
                    r.update(status="scheduled", post_id=hit["id"],
                             scheduled_at=due.isoformat(timespec="minutes") if due else "")
                    print(f"Подхвачен уже запланированный пост {r['id']} ({hit['id']})")
            if not dry:
                save(rows, header, csv_path)

        taken = [d for r in rows if r["network"] == net and status(r) in ("scheduled", "published")
                 for d in [P.parse_dt(r.get("scheduled_at"))] if d and d.date() == today]
        if len(taken) >= plan:
            print(f"[{net}] на сегодня уже всё запланировано ({len(taken)}/{plan}).")
            continue
        queued = len(remote) if remote is not None else 0
        if queued >= cfg("QUEUE_LIMIT"):
            print(f"::error::[{net}] очередь Buffer заполнена: {queued} из {cfg('QUEUE_LIMIT')}")
            red = True
            continue
        day_rng = rng or random.Random(f"social-{net}-{today.isoformat()}")
        when = make_time(net, today, now, taken, day_rng, recent_hours(net, rows, external, now + timedelta(days=1)))
        if not when:
            print(f"::warning::[{net}] в оставшуюся часть окна публикации поста не поместить")
            continue
        r = choose(rows, net)
        if not r:
            print(f"::error::[{net}] нет готовых строк (status=ready) с подходящим видом/ссылкой — "
                  f"пополните social.csv и запустите «Social images»")
            red = True
            continue
        errs = validate(r, root, when)
        if errs:
            print(f"::error::[{net}] строка {r['id']} пропущена: {'; '.join(errs)}")
            red = True
            continue
        text, fc = compose_text(r, when)
        line = f"{net:8} {r['id']:>6} [{r.get('kind')}] {when:%H:%M} Киев = {when.astimezone(ET):%H:%M} ET"
        if dry:
            print("DRY  " + line + f"\n     текст: {text[:90]}…" + (f"\n     1-й комментарий: {fc}" if fc else ""))
            continue
        url = image_url(r["image"])
        if not url_ok(url):
            print(f"::error::[{net}] {r['id']}: картинка недоступна по {url} (закоммичена ли она?)")
            red = True
            continue
        try:
            post_id, _ = create_social(client, net=net, text=text, first_comment=fc,
                                       image_rel=r["image"], due_utc=P.to_utc_z(when))
        except P.BufferError as e:
            msg = str(e)
            # Free-план Buffer: first comment — платная фича. Не валим весь job.
            if net == "facebook" and fc and ("first comment" in msg.lower() or "paid plan" in msg.lower()
                                              or "upgrade" in msg.lower() or "InvalidInput" in msg):
                print(f"::warning::[{net}] Buffer Free: first comment недоступен ({e}). "
                      f"Публикую {r['id']} без первого комментария (ссылка не уйдёт в FB).")
                try:
                    post_id, _ = create_social(client, net=net, text=text, first_comment="",
                                               image_rel=r["image"], due_utc=P.to_utc_z(when),
                                               use_first_comment=False)
                except P.BufferError as e2:
                    print(f"::error::[{net}] Buffer (без first comment): {e2}. Останавливаюсь; уже запланированное сохранено.")
                    save(rows, header, csv_path)
                    return 1
            else:
                print(f"::error::[{net}] Buffer: {e}. Останавливаюсь; уже запланированное сохранено.")
                save(rows, header, csv_path)
                return 1
        r.update(status="scheduled", scheduled_at=when.isoformat(timespec="minutes"), post_id=post_id)
        save(rows, header, csv_path)
        print("OK   " + line + f"  (post {post_id})")
    return 1 if red else 0


# ------------------------------------------------------------------ lint и plan
def lint(csv_path=CSV, root="."):
    rows, _ = load(csv_path)
    bad = ready = 0
    when = datetime(2026, 11, 2, 12, 0, tzinfo=P.kyiv())
    for r in rows:
        if status(r) != "ready":
            continue
        ready += 1
        msgs = validate(r, root, when)
        if msgs:
            bad += 1
            print(f"{r['id']}: " + "; ".join(msgs))
    left = {n: sum(1 for r in rows if r["network"] == n and status(r) == "ready") for n in cfg("CHANNELS")}
    new = {n: sum(1 for r in rows if r["network"] == n and status(r) == "new") for n in cfg("CHANNELS")}
    print(f"Готовых строк: {ready} (Facebook {left['facebook']}, X {left['x']}); ждут картинок: "
          f"Facebook {new['facebook']}, X {new['x']}; с замечаниями: {bad}")
    return 1 if bad else 0


def print_plan(days=30):
    external = load_external()
    today = P.now_kyiv()
    d0 = min(net_start(n) for n in cfg("CHANNELS"))
    d0 = max(d0, today.date())
    print("дата         Facebook                          X       (B = Buffer, время Киев/ET; m, t = Metricool, Typefully)")
    tot = {n: 0 for n in cfg("CHANNELS")}
    chron = {n: list(external.get(n, [])) for n in cfg("CHANNELS")}      # как в боевом запуске: час не повторяется
    for i in range(days):
        d = d0 + timedelta(days=i)
        cells = []
        for net in ("facebook", "x"):
            c = ""
            if posts_for_day(net, d, external):
                prev = sorted(x for x in chron[net] if x.date() < d)[-cfg("RECENT_HOURS_N"):]
                t = make_time(net, d, today - timedelta(days=2), [], random.Random(f"social-{net}-{d.isoformat()}"),
                              {x.astimezone(ET).hour for x in prev})
                c = f"B {t:%H:%M}/{t.astimezone(ET):%H:%M}" if t else "B ?"
                if t:
                    chron[net].append(t)
                tot[net] += 1
            ext = [e for e in external.get(net, []) if e.date() == d]
            if ext:
                c += (" " if c else "") + ("m" if net == "facebook" else "t") + f" {ext[0]:%H:%M}"
            cells.append(c)
        print(f"{d} {d:%a}  {cells[0]:<32} {cells[1]}")
    print(f"Всего за {days} дн. через Buffer: Facebook {tot['facebook']}, X {tot['x']}")


def main(argv):
    if "--plan" in argv:
        i = argv.index("--plan")
        print_plan(int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 30)
        return 0
    if "--lint" in argv:
        return lint()
    token = (os.environ.get("BUFFER_TOKEN") or "").strip()
    client = P.BufferClient(token) if token else None
    try:
        if "--check" in argv:
            if not client:
                print("::error::BUFFER_TOKEN не задан")
                return 1
            return 0 if check_connection(client) else 1
        if "--dry-run" in argv:
            return run("dry-run", client=client)
        if not client:
            print("::error::BUFFER_TOKEN не задан")
            return 1
        return run("run", client=client)
    except P.BufferAuthError as e:
        print(f"::error::Buffer отклонил ключ: {e}. Проверьте секрет BUFFER_TOKEN.")
        return 1
    except P.BufferError as e:
        print(f"::error::Buffer: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
