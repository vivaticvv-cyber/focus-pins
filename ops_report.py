"""Автоматический отчёт о состоянии конвейера: ops/auto-status.md (перезаписывается). Только чтение данных репозитория.

Запуск: python ops_report.py   (ежедневно — workflow «Ops report»; можно вручную)
Если рядом лежит ops/_runs.json (его делает workflow через gh), в отчёт попадают последние запуски Actions.
Цель: Грок и Claude видят одни и те же честные числа без траты токенов на подсчёт.
"""
import contextlib
import csv
import datetime
import glob
import io
import json
import os
import re
from datetime import date, timedelta

import publish as P

END = date(2027, 1, 14)
INFO_SHARE = 0.78          # доля информационных пинов (промо ≤ 1 из 4)
PAD = "small visible step is still progress"
MIN_RUNWAY_DAYS = 14       # порог: ниже — пора писать партию


def runway(unpub, share, start):
    """Дата, когда закончатся неопубликованные строки, и сколько нужно до END."""
    d, acc, out = start, 0.0, None
    while d <= END:
        acc += P.pins_for_day(d) * share
        if out is None and acc > unpub:
            out = d
        d += timedelta(1)
    return out, max(0, round(acc - unpub))


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    today = (now + timedelta(hours=3)).date()
    rows, _ = P.load_rows("pins.csv")
    st = lambda r: P.status(r)
    c = {}
    for r in rows:
        c[st(r)] = c.get(st(r), 0) + 1
    info = [r for r in rows if st(r) in ("new", "ready") and P.board_kind(r.get("board")) == "info"]
    promo = [r for r in rows if st(r) in ("new", "ready") and P.board_kind(r.get("board")) != "info"]
    ri, need_i = runway(len(info), INFO_SHARE, today + timedelta(1))
    rp, need_p = runway(len(promo), 1 - INFO_SHARE, today + timedelta(1))
    pad = [r["id"] for r in rows if PAD in (r.get("description") or "")]
    odd = [r["id"] for r in rows if st(r) == "new" and ((r.get("scheduled_at") or "").strip() or (r.get("buffer_post_id") or "").strip())]
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        bad = P.lint("pins.csv", images_dir="images")
    L = [f"# Auto status (ops_report.py) — {now:%Y-%m-%d %H:%M} UTC", ""]
    L += ["## Pinterest (pins.csv)",
          f"- Строк {len(rows)}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())),
          f"- Неопубликованных информационных (new+ready): {len(info)}; хватит до {ri or '>' + str(END)}; до {END} докупить ≈ {need_i}",
          f"- Неопубликованных промо (new+ready): {len(promo)}; хватит до {rp or '>' + str(END)}; до {END} докупить ≈ {need_p}"]
    days_i = (ri - today).days if ri else 999
    L.append(f"- Запас информационных: {days_i} дн. → " + ("ПОРА ПИСАТЬ ПАРТИЮ" if days_i < MIN_RUNWAY_DAYS else "в норме"))
    L.append(f"- lint pins.csv: {'замечания есть (запусти Daily pins → lint)' if bad else 'замечаний нет'}")
    L.append(f"- Строк new со сдвинутыми колонками (служебные поля заполнены): {len(odd)}" + (f" (id {', '.join(odd)}) → исправить патчем" if odd else ""))
    L.append(f"- Описаний с фразой-добивкой «small visible step»: {len(pad)}" + (f" (id {', '.join(pad[:12])}{'…' if len(pad) > 12 else ''})" if pad else ""))
    # social
    import social as S
    srows = S.load()
    L += ["", "## Facebook/X (social.csv)"]
    groups = {"S (Facebook, Buffer)": lambda i: i.startswith("S") and not i.startswith("SX") and not i.startswith("S1"),
              "SX (X, Buffer)": lambda i: i.startswith("SX") and not i.startswith("SX1"),
              "M (Facebook, Metricool)": lambda i: i.startswith("M")}
    for name, f in groups.items():
        g = [r for r in srows if f(r["id"])]
        rdy = [r for r in g if r["status"] == "ready"]
        noimg = [r["id"] for r in rdy if not (r.get("image") or "").strip()]
        new = sum(r["status"] == "new" for r in g)
        L.append(f"- {name}: ready {len(rdy)} (без картинки: {len(noimg)}), new {new}, scheduled/published {sum(r['status'] in ('scheduled', 'published') for r in g)}")
        if noimg:
            L.append(f"  - ОШИБКА: ready без картинки → publish упадёт: {', '.join(noimg)} (нужно status=new)")
    # очереди партий
    rej = sorted(glob.glob("batches/rejected_*.csv"))
    have = {r["id"] for r in rows} | {r["id"] for r in srows}
    L += ["", "## Партии"]
    L.append("- Файлов в корне, ждущих слияния: " + (", ".join(sorted(glob.glob("pins_batch_*.csv") + glob.glob("pins_patch_*.csv") + glob.glob("social_batch_*.csv"))) or "нет"))
    if rej:
        for f in rej:
            with open(f, encoding="utf-8-sig", newline="") as fh:
                ids = [r.get("id") for r in csv.DictReader(fh) if r.get("id") not in have]
            if not ids:
                continue
            L.append(f"- Отклонённые строки: {os.path.basename(f)} → id {', '.join(ids)} (нужно исправить и отправить как *_fix.csv)")
    if not any(l.startswith("- Отклонённые строки") for l in L):
        L.append("- Отклонённых строк нет")
    # запуски Actions
    p = "ops/_runs.json"
    if os.path.exists(p):
        try:
            runs = json.load(open(p, encoding="utf-8"))
            L += ["", "## Последние запуски Actions"]
            for r in runs[:10]:
                L.append(f"- {r['createdAt'][5:16]} {r['name']}: {r.get('conclusion') or r.get('status')}")
        except Exception as e:
            L.append(f"- не удалось прочитать ops/_runs.json: {e}")
    os.makedirs("ops", exist_ok=True)
    open("ops/auto-status.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
