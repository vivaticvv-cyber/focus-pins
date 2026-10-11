"""FOCUS social: отдельные картинки и тексты для Facebook и X (не повторяют пины Pinterest).

Запуск (все режимы безопасны для Pinterest-конвейера: generate.py и publish.py не меняются):
  python social.py --demo            пробные картинки: по 4 на сеть -> test/social_demo/ + contact_sheet.jpg
  python social.py --stock [N]       сделать картинки для N строк social.csv со status=new (по умолчанию 12)
  python social.py --lint            проверить social.csv (длины, ссылки, хэштеги, дубли)
  python social.py --links           показать, какие ссылки (с метками и кодом BF30) получили бы посты сегодня

Размеры: Facebook 1080x1350 (4:5), X 1600x900 (16:9). Нейросеть рисует сцену (Cloudflare Workers AI, как в generate.py),
надпись и фирменная плашка добавляются поверх. Строки kind=showcase — готовые картинки из реальных файлов (showcase.py).
"""
import csv
import os
import random
import shutil
import sys
import zlib
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFilter, ImageStat

import generate as G          # те же стили, шрифты и источник картинок, что и у пинов
import publish as P

CSV = "social.csv"
FIELDS = ["id", "network", "kind", "topic", "hook", "text", "first_comment", "scene_prompt", "style", "layout",
          "link_key", "status", "image", "scheduled_at", "post_id"]

NET = {
    "facebook": dict(w=1080, h=1350, gen=(1024, 1280), layouts=["plate_top", "bare_top", "banner_bottom"],
                     hook_words=6, zone="top",
                     comp="Vertical 4:5 poster composition: the main subject sits in the lower two thirds of the frame, "
                          "and the top third is a calm, quiet area of plain background color."),
    "x": dict(w=1600, h=900, gen=(1344, 768), layouts=["left_plate", "left_bare", "none"],
              hook_words=4, zone="left",
              comp="Wide horizontal composition: the main subject sits in the right half of the frame, and the left "
                   "40 percent of the frame is a calm, quiet area of plain background color."),
}

# ссылки: ключ -> (базовый адрес, платный товар Gumroad?)
LINKS = {
    "trial": ("https://focus-mini.pages.dev/", False),
    "mini": ("https://vivatic.gumroad.com/l/dwshkr", False),
    "planner": ("https://vivatic.gumroad.com/l/seqen", True),
    "soft": ("https://vivatic.gumroad.com/l/soft-structure", True),
    "bundle": ("https://vivatic.gumroad.com/l/premium-pack", True),
}
SALE = dict(code="BF30", start="2026-11-26T10:00", end="2026-12-01T10:00")     # время Киева; код на платные товары
UTM_SOURCE = {"facebook": "facebook", "x": "x"}


# ------------------------------------------------------------------ ссылки
def sale_active(now=None):
    now = now or P.now_kyiv()
    s = datetime.fromisoformat(SALE["start"]).replace(tzinfo=P.kyiv())
    e = datetime.fromisoformat(SALE["end"]).replace(tzinfo=P.kyiv())
    return s <= now < e


def build_link(link_key, network, row_id, kind="post", now=None):
    """Адрес с метками UTM (не видны в тексте картинки); во время распродажи — платные товары со скидочным кодом."""
    base, paid = LINKS[link_key]
    if paid and sale_active(now):
        base = f"{base}/{SALE['code']}"
    q = urlencode({"utm_source": UTM_SOURCE[network], "utm_medium": "social", "utm_campaign": kind,
                   "utm_content": row_id})
    return f"{base}?{q}"


# ------------------------------------------------------------------ CSV
def load():
    with open(CSV, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        rows = [dict(r) for r in rd]
    return rows


def save(rows):
    tmp = CSV + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, restval="", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, CSV)


# ------------------------------------------------------------------ картинка
def pick_style(row, idx):
    k = (row.get("style") or "").strip()
    return k if k in G.STYLES else G.STYLE_ORDER[idx % len(G.STYLE_ORDER)]


def build_prompt(scene, style, net):
    scene = scene.replace("{mascot}", G.MASCOT).strip().rstrip(".")
    focus = f" {style['focus']}" if style.get("focus") else ""
    return f"{scene}. {style['medium']}{focus} {style['light']} {style['palette']} {NET[net]['comp']}"


def compose(art_path, hook, out_path, net, skey, layout, fkey):
    cfg, st = NET[net], G.STYLES[skey]
    W, H = cfg["w"], cfg["h"]
    ink, plate, acc = G.hex2rgb(st["ink"]), G.hex2rgb(st["plate"]), G.hex2rgb(st["accent"])
    img = Image.open(art_path).convert("RGB")
    # привести к нужному соотношению сторон (обрезка по центру), затем к размеру
    tw, th = img.size
    target = W / H
    if tw / th > target:
        nw = int(th * target); img = img.crop(((tw - nw) // 2, 0, (tw - nw) // 2 + nw, th))
    else:
        nh = int(tw / target); img = img.crop((0, (th - nh) // 2, tw, (th - nh) // 2 + nh))
    img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    hook = (hook or "").strip()

    if hook and layout in ("plate_top", "banner_bottom"):
        if layout == "plate_top":
            fnt, lines, size = G.fit(d, hook, fkey, W - 220, max_lines=3, start=108)
            lh = int(size * 1.18); ph = lh * len(lines) + 64; y0 = 60
            d.rounded_rectangle((50, y0, W - 50, y0 + ph), radius=64, fill=plate + (240,), outline=acc, width=6)
            G.draw_lines(d, lines, fnt, W // 2, y0 + 32, lh, ink)
        else:
            fnt, lines, size = G.fit(d, hook, fkey, W - 160, max_lines=2, start=100)
            lh = int(size * 1.2); bh = lh * len(lines) + 90; y0 = H - bh
            d.rectangle((0, y0, W, H), fill=ink + (245,)); d.rectangle((0, y0, W, y0 + 10), fill=acc + (255,))
            G.draw_lines(d, lines, fnt, W // 2, y0 + 45, lh, plate)
    elif hook and layout == "bare_top":
        fnt, lines, size = G.fit(d, hook, fkey, W - 140, max_lines=3, start=116)
        lh = int(size * 1.15)
        light_bg = G.lum(ImageStat.Stat(img.crop((0, 40, W, 40 + lh * len(lines) + 60))).mean[:3]) > 150
        fill = ink if (light_bg and G.lum(ink) < 140) else ((43, 43, 43) if light_bg else (255, 248, 236))
        glow = (255, 248, 236, 200) if light_bg else (20, 30, 40, 170)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        G.draw_lines(ImageDraw.Draw(layer), lines, fnt, W // 2 + 3, 75 + 5, lh, glow)
        img = Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(9))).convert("RGB")
        G.draw_lines(ImageDraw.Draw(img, "RGBA"), lines, fnt, W // 2, 75, lh, fill)
    elif hook and layout in ("left_plate", "left_bare"):
        box_w = int(W * 0.44)
        fnt, lines, size = G.fit(d, hook, fkey, box_w - 100, max_lines=4, start=120, min_size=64)
        lh = int(size * 1.18); ph = lh * len(lines) + 64; y0 = (H - ph) // 2
        if layout == "left_plate":
            d.rounded_rectangle((50, y0, 50 + box_w, y0 + ph), radius=56, fill=plate + (240,), outline=acc, width=6)
            G.draw_lines(d, lines, fnt, 50 + box_w // 2, y0 + 32, lh, ink)
        else:
            light_bg = G.lum(ImageStat.Stat(img.crop((40, y0, 40 + box_w, y0 + ph)).convert("RGB")).mean[:3]) > 150
            fill = ink if (light_bg and G.lum(ink) < 140) else ((43, 43, 43) if light_bg else (255, 248, 236))
            glow = (255, 248, 236, 200) if light_bg else (20, 30, 40, 170)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            G.draw_lines(ImageDraw.Draw(layer), lines, fnt, 50 + box_w // 2 + 3, y0 + 8, lh, glow)
            img = Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(9))).convert("RGB")
            G.draw_lines(ImageDraw.Draw(img, "RGBA"), lines, fnt, 50 + box_w // 2, y0 + 3, lh, fill)
    # маленький стикер FOCUS в нижнем углу, противоположном тексту
    badge(img, st, net, layout)
    img.save(out_path, "JPEG", quality=90, optimize=True)


def badge(img, st, net, layout):
    W, H = img.size
    acc = G.hex2rgb(st["accent"])
    txt = (255, 255, 255) if G.lum(acc) < 175 else (43, 43, 43)
    bw, bh = (230, 84) if net == "x" else (260, 94)
    b = Image.new("RGBA", (bw + 30, bh + 30), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle((16, 18, bw + 16, bh + 18), radius=34, fill=(0, 0, 0, 55))
    b = b.filter(ImageFilter.GaussianBlur(4))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle((10, 8, bw + 10, bh + 8), radius=34, fill=acc)
    bd.text(((bw + 20) // 2, (bh + 16) // 2), "FOCUS", font=G.get_font("fredoka", 56 if net == "x" else 62), fill=txt,
            anchor="mm")
    b = b.rotate(5, expand=True, resample=Image.BICUBIC)
    x = W - b.width - 18
    y = H - b.height - 18
    if net == "facebook" and layout == "banner_bottom":
        y = 18
    img.paste(b, (x, y), b)


def make_image(row, idx, state, out_path):
    net = row["network"]
    skey = pick_style(row, idx)
    layout = (row.get("layout") or "").strip()
    if layout not in NET[net]["layouts"]:
        layout = NET[net]["layouts"][idx % len(NET[net]["layouts"])]
    rng = random.Random(zlib.crc32(f"{row['id']}-{net}".encode()))
    fkey = rng.choice(G.STYLES[skey]["fonts"])
    G.GEN_W, G.GEN_H = NET[net]["gen"]
    raw = str(out_path) + ".raw.png"
    src = G.generate(build_prompt(row["scene_prompt"], G.STYLES[skey], net), raw, state)
    compose(raw, row["hook"], out_path, net, skey, layout, fkey)
    os.remove(raw)
    return src, f"{skey}/{layout}/{fkey}"


# ------------------------------------------------------------------ режимы
def run_demo(rows):
    shutil.rmtree("test/social_demo", ignore_errors=True)
    os.makedirs("test/social_demo", exist_ok=True)
    state, done, paths = {"cf_ok": True, "hf_used": 0}, 0, []
    styles = ["clay3d", "felt", "gouache", "shadowbox"]
    for net in ("facebook", "x"):
        cand = [r for r in rows if r["network"] == net and r["kind"] != "showcase"][:4]
        for i, r in enumerate(cand):
            r = dict(r); r["style"] = styles[i % len(styles)]; r["layout"] = ""
            out = f"test/social_demo/{net}_{i + 1}_{r['style']}.jpg"
            try:
                src, combo = make_image(r, i, state, out)
                print(f"demo {net} {i + 1}: OK via {src} [{combo}]")
                paths.append(out); done += 1
            except Exception as e:
                print(f"demo {net} {i + 1}: FAIL {e}", file=sys.stderr)
    if paths:
        sheet = Image.new("RGB", (4 * 300, 375 + 169 + 20), (245, 245, 245))
        k = {"facebook": 0, "x": 0}
        for p in paths:
            im = Image.open(p)
            if "facebook" in p:
                sheet.paste(im.resize((300, 375)), (k["facebook"] * 300, 0)); k["facebook"] += 1
            else:
                sheet.paste(im.resize((300, 169)), (k["x"] * 300, 385)); k["x"] += 1
        sheet.save("test/social_demo/contact_sheet.jpg", "JPEG", quality=88)
    if done == 0:
        sys.exit(1)


def run_stock(rows, limit):
    state, done = {"cf_ok": True, "hf_used": 0}, 0
    for idx, r in enumerate(rows):
        if done >= limit:
            break
        if P.status(r) != "new" or r["kind"] == "showcase":
            continue
        out = Path("images/social") / r["network"] / f"{r['id']}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            src, combo = make_image(r, idx, state, out)
        except Exception as e:
            print(f"{r['id']} skipped: {e}", file=sys.stderr)
            break
        r["status"] = "ready"; r["image"] = str(out)
        save(rows); done += 1
        print(f"done {r['id']} ({r['network']}) via {src} [{combo}]")
    new_left = sum(1 for r in rows if P.status(r) == "new" and r["kind"] != "showcase")
    print(f"Сделано {done}; осталось строк new: {new_left}")
    if limit > 0 and done == 0 and new_left > 0:
        sys.exit(1)


def lint(rows):
    bad, seen = 0, {}
    for r in rows:
        m = []
        net = r["network"]
        if net not in NET:
            m.append("network должен быть facebook или x")
        else:
            hook_words = len((r.get("hook") or "").split())
            if hook_words > NET[net]["hook_words"]:
                m.append(f"надпись {hook_words} слов (максимум {NET[net]['hook_words']})")
        t = (r.get("text") or "").strip()
        tags = [w for w in t.split() if w.startswith("#")]
        if len(tags) > 2:
            m.append(f"хэштегов {len(tags)} (максимум 2)")
        if net == "x":
            n = len(t) + (23 + 1 if (r.get("link_key") or "").strip() else 0)
            if n > 280:
                m.append(f"текст {n} симв. с ссылкой (> 280)")
        if net == "facebook":
            if "http" in t:
                m.append("в теле поста Facebook не должно быть ссылки (она идёт в первый комментарий)")
            if not (180 <= len(t) <= 700):
                m.append(f"текст {len(t)} симв. (нужно 180–700)")
        if t in seen:
            m.append(f"текст совпадает со строкой {seen[t]}")
        seen.setdefault(t, r["id"])
        if (r.get("link_key") or "") and r["link_key"] not in LINKS:
            m.append(f"неизвестный link_key {r['link_key']}")
        scene = (r.get("scene_prompt") or "").lower()
        if r["kind"] != "showcase":
            bw = [w for w in ("laptop", "screen", "phone", "computer", "hand ", "hands", "person", "people", "man ",
                              "woman", "girl", "boy ", "human", "face") if w in scene + " "]
            if bw:
                m.append("в сцене нежелательные слова: " + ", ".join(w.strip() for w in bw))
        if m:
            bad += 1
            print(f"{r['id']}: " + "; ".join(m))
    fb = sum(1 for r in rows if r["network"] == "facebook"); x = sum(1 for r in rows if r["network"] == "x")
    print(f"Строк: {len(rows)} (Facebook {fb}, X {x}), с замечаниями: {bad}")
    return 1 if bad else 0


def show_links(rows):
    for r in rows:
        if (r.get("link_key") or "").strip():
            print(f"{r['id']:>6} {r['network']:<8} {build_link(r['link_key'], r['network'], r['id'], r['kind'])}")
    print("Распродажа сейчас активна:", sale_active())


def main(argv):
    rows = load()
    if "--lint" in argv:
        return lint(rows)
    if "--links" in argv:
        return show_links(rows)
    if "--demo" in argv:
        return run_demo(rows)
    if "--stock" in argv:
        i = argv.index("--stock")
        n = int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 12
        return run_stock(rows, n)
    print(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
