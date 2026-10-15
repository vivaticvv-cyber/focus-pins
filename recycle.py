"""FOCUS autopilot: автоматическое пополнение очереди контента (без участия человека).

Когда готовых и новых строк в pins.csv / social.csv остаётся меньше, чем нужно на ближайшие дни по плану
публикаций, добавляет «свежие версии» уже опубликованных материалов: тот же текст (проверенный и одобренный),
но новая строка со status=new — generate.py / social.py нарисуют для неё НОВУЮ картинку (другой стиль и
раскладка выбираются по номеру строки). Pinterest прямо поощряет свежие пины на старый материал.

Правила:
- Берутся только опубликованные строки; тема не повторяется, пока её копия ещё ждёт публикации.
- Пины: тема возвращается не раньше чем через PINS_MIN_AGE_DAYS дней; продуктовые пины (картинки из
  pinterest_product.py) не копируются.
- Соцсети: тема возвращается не раньше чем через SOCIAL_MIN_AGE_DAYS дней; витринные (showcase) не копируются.
- Копии помечаются в колонке topic суффиксом « ↻N» (N — номер повтора).

Запуск:  python recycle.py [--dry-run]
"""
import csv
import os
import re
import sys
from datetime import datetime, timedelta

import publish as P

PINS_RUNWAY_DAYS = 21           # держать строк минимум на столько дней вперёд по плану
SOCIAL_RUNWAY_DAYS = 30
PINS_MIN_AGE_DAYS = 21
SOCIAL_MIN_AGE_DAYS = 28
MAX_ADD_PINS = 60               # не больше за один прогон
MAX_ADD_SOCIAL = 20
MARK = " ↻"
BASE_RE = re.compile(r"\s*↻\d+$")


def base(topic):
    return BASE_RE.sub("", (topic or "").strip())


def next_topic(topic, n):
    return f"{base(topic)}{MARK}{n}"


def pick_sources(rows, min_age_days, now, exclude, need):
    """Группы по базовой теме -> оригиналы для копирования (самые давние сначала)."""
    groups = {}
    for r in rows:
        groups.setdefault(base(r.get("topic")), []).append(r)
    cands = []
    for b, rs in groups.items():
        if any(P.status(r) in ("new", "ready", "scheduled") for r in rs):
            continue                                           # копия этой темы ещё в очереди
        last = max((P.parse_dt(r.get("scheduled_at")) for r in rs if P.status(r) == "published"
                    and P.parse_dt(r.get("scheduled_at"))), default=None)
        if last is None or last > now - timedelta(days=min_age_days):
            continue
        src = rs[0]                                            # первая строка группы — оригинал
        if exclude(src):
            continue
        cands.append((last, len(rs), src))
    cands.sort(key=lambda t: (t[1], t[0]))                     # реже повторявшиеся и самые давние — первыми
    return [(src, n) for _, n, src in cands[:need]]


# ------------------------------------------------------------------ Pinterest
def recycle_pins(now, dry=False, path="pins.csv"):
    rows, header = P.load_rows(path)
    need_total = sum(P.pins_for_day((now + timedelta(days=i)).date()) for i in range(0, PINS_RUNWAY_DAYS))
    have = sum(1 for r in rows if P.status(r) in ("new", "ready"))
    if have >= need_total:
        print(f"[pins] запас достаточен: {have} строк на {need_total} пинов за {PINS_RUNWAY_DAYS} дн.")
        return 0
    want = min(need_total - have + 10, MAX_ADD_PINS)
    srcs = pick_sources(rows, PINS_MIN_AGE_DAYS, now,
                        lambda r: (r.get("scene_prompt") or "").lower().startswith("product pin"), want)
    nid = max(int(r["id"]) for r in rows) + 1
    added = 0
    for src, n in srcs:
        c = dict(src)
        c.update(id=str(nid), topic=next_topic(src.get("topic"), n), status="new", style="", layout="",
                 link="", scheduled_at="", buffer_post_id="")
        rows.append(c)
        nid += 1
        added += 1
    print(f"[pins] запас {have} < нужно {need_total}: добавлено свежих версий {added} (запрошено {want})")
    if added < min(need_total - have, MAX_ADD_PINS):
        print(f"::warning::[pins] не хватает подходящих тем для повтора ({added} из {min(need_total - have, MAX_ADD_PINS)}): "
              f"добавьте новые строки в pins.csv")
    if added and not dry:
        P.save_rows(rows, header, path)
    return added


# ------------------------------------------------------------------ Facebook / X
def recycle_social(now, dry=False, path="social.csv"):
    import social_publish as SP
    rows, header = SP.load(path)
    external = SP.load_external()
    added_total = 0
    for net, prefix in (("facebook", "SR"), ("x", "XR")):
        mine = [r for r in rows if r["network"] == net and not r["id"].startswith("M")]
        need = sum(SP.posts_for_day(net, (now + timedelta(days=i)).date(), external)
                   for i in range(0, SOCIAL_RUNWAY_DAYS))
        have = sum(1 for r in mine if P.status(r) in ("new", "ready") and r.get("kind") != "showcase")
        if have >= need:
            print(f"[{net}] запас достаточен: {have} строк на {need} постов за {SOCIAL_RUNWAY_DAYS} дн.")
            continue
        want = min(need - have + 3, MAX_ADD_SOCIAL)
        srcs = pick_sources(mine, SOCIAL_MIN_AGE_DAYS, now, lambda r: r.get("kind") == "showcase", want)
        nums = [int(m.group(1)) for r in rows
                for m in [re.match(rf"^{prefix}(\d+)$", r["id"])] if m]
        nid = max(nums, default=0) + 1
        added = 0
        for src, n in srcs:
            c = dict(src)
            c.update(id=f"{prefix}{nid:03d}", topic=next_topic(src.get("topic"), n), status="new", style="",
                     layout="", image="", scheduled_at="", post_id="")
            rows.append(c)
            nid += 1
            added += 1
        print(f"[{net}] запас {have} < нужно {need}: добавлено свежих версий {added}")
        if added < min(need - have, MAX_ADD_SOCIAL):
            print(f"::warning::[{net}] не хватает подходящих тем для повтора ({added} из {min(need - have, MAX_ADD_SOCIAL)}): "
                  f"добавьте новые строки в social.csv")
        added_total += added
    if added_total and not dry:
        SP.save(rows, header, path)
    return added_total


def main(argv):
    dry = "--dry-run" in argv
    now = P.now_kyiv()
    n = 0
    if os.path.exists("pins.csv"):
        n += recycle_pins(now, dry)
    if os.path.exists("social.csv"):
        n += recycle_social(now, dry)
    print(f"Итого добавлено строк: {n}" + (" (dry-run, файлы не менялись)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
