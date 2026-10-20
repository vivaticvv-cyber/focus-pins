"""Продуктовые пины Pinterest по таблице product_specs.csv — без нейросети и без участия Claude.

Как это работает:
  1) в pins.csv добавляется строка пина: board «FOCUS – ADHD Planner», status=new,
     scene_prompt = product pin (pinterest_product.py), link = страница товара, pin_title/description как обычно;
  2) в product_specs.csv добавляется строка с тем же id: раскладка, палитра, заголовок на картинке, какие страницы/стикеры/экраны;
  3) этот скрипт (Autopilot запускает его каждый раз) рисует images/<id>.jpg из реальных материалов assets/showcase/
     и ставит строке status=ready.
Если строки в product_specs.csv нет или в ней ошибка, строка остаётся new, а причина печатается ::warning:: (запуск не падает).
Запуск вручную: python product_pins.py [--check]   (--check только проверяет, ничего не рисует)
"""
import csv
import os
import sys

import pinterest_product as PP
import publish as P

SPEC_FILE = "product_specs.csv"
MARK = "product pin"

FMT = {"pdf": PP.FMT_PDF, "trial": PP.FMT_TRIAL, "html": PP.FMT_HTML, "stick": PP.FMT_STICK, "bundle": PP.FMT_BUNDLE,
       "a4": "Undated  ·  fillable  ·  A4, A5, Letter", "pages48": "48 pages  ·  A4, A5, Letter"}
STRIP = {"pdf": PP.STRIP_PDF, "html": PP.STRIP_HTML, "bundle": PP.STRIP_BUNDLE}
WALLS = {"wall": PP.WALL, "wall2": PP.WALL2, "wall3": PP.WALL3}
PALS = set(PP.PALETTES)
REQ = {"page_stickers": ["page", "stickers"], "duo_pages": ["pages"], "fan3": ["pages"], "closeup": ["page", "box", "stickers"],
       "phone_duo": [], "phone_solo": ["screen", "pills"], "screen": ["screen"], "sticker_wall": ["stickers"], "bundle": []}


def _list(v):
    return [x.strip() for x in (v or "").split("|") if x.strip()]


def build(row):
    """Строка CSV -> spec для pinterest_product.render; ошибки -> ValueError с понятным текстом."""
    s = {"id": int(row["id"]), "layout": (row.get("layout") or "").strip(), "pal": (row.get("pal") or "").strip()}
    if s["layout"] not in PP.LAYOUTS:
        raise ValueError(f"layout «{s['layout']}» неизвестен (есть: {', '.join(PP.LAYOUTS)})")
    if s["pal"] not in PALS:
        raise ValueError(f"pal «{s['pal']}» неизвестна (есть: {', '.join(sorted(PALS))})")
    head = (row.get("headline") or "").replace("\\n", "\n").strip()
    lines = head.split("\n")
    if not (1 <= len(lines) <= 2) or any(len(x) > 24 or not x.strip() for x in lines):
        raise ValueError("headline: 1–2 строки через \\n, каждая ≤ 24 символов")
    s["headline"] = head
    key = (row.get("fmt") or "").strip()
    s["fmt"] = FMT.get(key, key)
    if not s["fmt"] or len(s["fmt"]) > 48:
        raise ValueError("fmt: ключ (pdf, trial, html, stick, bundle, a4, pages48) или текст ≤ 48 символов")
    st = (row.get("strip") or "").strip()
    s["strip"] = STRIP.get(st, st)
    if not s["strip"]:
        raise ValueError("strip: ключ (pdf, html, bundle)")
    if row.get("page"):
        s["page"] = row["page"].strip()
    if row.get("pages"):
        s["pages"] = _list(row["pages"])
    st_raw = (row.get("stickers") or "").strip()
    if st_raw:
        s["stickers"] = WALLS[st_raw] if st_raw in WALLS else _list(st_raw)
    if row.get("screen"):
        s["screen"] = row["screen"].strip()
    if row.get("pills"):
        s["pills"] = _list(row["pills"])
    if row.get("side"):
        s["side"] = row["side"].strip()
    if row.get("box"):
        b = [float(x) for x in row["box"].split(",")]
        if len(b) != 4 or not all(0 <= x <= 1 for x in b) or b[0] >= b[2] or b[1] >= b[3]:
            raise ValueError("box: четыре числа 0–1 через запятую: x0,y0,x1,y1")
        s["box"] = tuple(b)
    for k in REQ[s["layout"]]:
        if not s.get(k):
            raise ValueError(f"для layout {s['layout']} обязательно поле {k}")
    need = {"fan3": 3, "duo_pages": 2}.get(s["layout"])
    if need and len(s.get("pages", [])) != need:
        raise ValueError(f"для {s['layout']} нужно ровно {need} страницы в pages")
    if s["layout"] == "page_stickers" and len(s.get("stickers", [])) < 3:
        raise ValueError("для page_stickers нужно 3 стикера в stickers")
    if s["layout"] in ("closeup", "duo_pages") and s["layout"] == "closeup" and len(s.get("stickers", [])) < 2:
        raise ValueError("для closeup нужно 2 стикера")
    for p in ([s["page"]] if s.get("page") else []) + s.get("pages", []):
        if not os.path.exists(os.path.join("assets", "showcase", "pages", p + ".png")):
            raise ValueError(f"нет страницы assets/showcase/pages/{p}.png")
    for n in (s.get("stickers", []) if not isinstance(s.get("stickers"), str) else []):
        if not os.path.exists(os.path.join("assets", "showcase", "stickers", n + ".png")):
            raise ValueError(f"нет стикера assets/showcase/stickers/{n}.png")
    if s.get("screen") and not os.path.exists(os.path.join("assets", "showcase", "screens", s["screen"])):
        raise ValueError(f"нет экрана assets/showcase/screens/{s['screen']}")
    return s


def main(argv):
    check = "--check" in argv
    if not os.path.exists(SPEC_FILE):
        print(f"{SPEC_FILE} нет — продуктовых пинов для отрисовки нет.")
        return 0
    with open(SPEC_FILE, encoding="utf-8-sig", newline="") as f:
        specs = {r["id"].strip(): r for r in csv.DictReader(f) if (r.get("id") or "").strip()}
    rows, header = P.load_rows("pins.csv")
    done = bad = 0
    for r in rows:
        todo = P.status(r) == "new" or (P.status(r) == "ready" and not os.path.exists(f"images/{r['id']}.jpg"))
        if not todo or not (r.get("scene_prompt") or "").strip().lower().startswith(MARK):
            continue
        spec_row = specs.get(r["id"])
        if not spec_row:
            print(f"::warning::пин {r['id']}: нет строки в {SPEC_FILE} — остаётся new")
            bad += 1
            continue
        try:
            spec = build(spec_row)
            if check:
                print(f"OK (проверка) пин {r['id']}: {spec['layout']}")
                continue
            os.makedirs("images", exist_ok=True)
            PP.render(spec).save(f"images/{r['id']}.jpg", "JPEG", quality=92, optimize=True)
            r["status"] = "ready"
            done += 1
            print(f"OK пин {r['id']}: {spec['layout']} -> images/{r['id']}.jpg")
        except Exception as e:  # одна плохая строка не блокирует остальные
            print(f"::warning::пин {r['id']}: {e}")
            bad += 1
    if done:
        P.save_rows(rows, header, "pins.csv")
    print(f"Продуктовых пинов нарисовано: {done}, с ошибками: {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
