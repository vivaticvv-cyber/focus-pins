"""FOCUS pins v3: разнообразные иллюстрации FLUX.2 klein 4B + разные раскладки заголовков + «склад» на 2–3 дня.

Источники картинок: Cloudflare Workers AI (основной) -> HF Space (резерв, без повторов).
Режимы:
  python generate.py          обычный: докручивает «склад» — держит готовые картинки (status=ready)
                              на STOCK_DAYS дней вперёд по плану publish.py; строки new -> images/N.jpg, status=ready
  python generate.py --test   первые 3 строки pins.csv -> test/ (pins.csv не меняется)
  python generate.py --demo   по одной картинке на КАЖДЫЙ стиль -> test/demo_*.jpg + contact_sheet.jpg
Переменные окружения: PINS_PER_RUN (принудительно сделать ровно N картинок), GEN_MAX_PER_RUN (потолок за прогон, 12),
STOCK_DAYS (3), START_DATE, HF_MAX_PER_RUN (1), CF_GUIDANCE.
Необязательные колонки pins.csv: pin_title, style (ключ стиля), layout (ключ раскладки).
"""
import base64, csv, io, os, random, shutil, sys, time, urllib.request
from pathlib import Path
import requests
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

import publish as P

SPACE = "black-forest-labs/FLUX.2-klein-4B"
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
PINS_PER_RUN = (os.environ.get("PINS_PER_RUN") or "").strip()      # пусто = по складу
GEN_MAX_PER_RUN = int(os.environ.get("GEN_MAX_PER_RUN") or "12")
HF_MAX_PER_RUN = int(os.environ.get("HF_MAX_PER_RUN", "1"))
CF_GUIDANCE = os.environ.get("CF_GUIDANCE", "").strip()   # пусто = по умолчанию Cloudflare
W, H = 1000, 1500
GEN_W, GEN_H = 1024, 1536
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# ---------- шрифты (скачиваются один раз в fonts/, при сбое — запасной Fredoka) ----------
FONTS = {
    "fredoka": dict(file="Fredoka.ttf", url=GF + "fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf", axes=[700, 100]),
    "lilita": dict(file="LilitaOne-Regular.ttf", url=GF + "lilitaone/LilitaOne-Regular.ttf"),
    "archivo": dict(file="ArchivoBlack-Regular.ttf", url=GF + "archivoblack/ArchivoBlack-Regular.ttf"),
    "bebas": dict(file="BebasNeue-Regular.ttf", url=GF + "bebasneue/BebasNeue-Regular.ttf", upper=True),
    "poppins": dict(file="Poppins-Bold.ttf", url=GF + "poppins/Poppins-Bold.ttf"),
    "caveat": dict(file="CaveatBrush-Regular.ttf", url=GF + "caveatbrush/CaveatBrush-Regular.ttf"),
    "dmserif": dict(file="DMSerifDisplay-Regular.ttf", url=GF + "dmserifdisplay/DMSerifDisplay-Regular.ttf"),
    "sniglet": dict(file="Sniglet-ExtraBold.ttf", url=GF + "sniglet/Sniglet-ExtraBold.ttf"),
    "bowlby": dict(file="BowlbyOne-Regular.ttf", url=GF + "bowlbyone/BowlbyOne-Regular.ttf"),
}
_fc = {}


def get_font(key, size):
    spec = FONTS.get(key) or FONTS["fredoka"]
    k = (key, size)
    if k in _fc:
        return _fc[k]
    path = Path(spec["file"]) if key == "fredoka" else Path("fonts") / spec["file"]
    try:
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(spec["url"], path)
        f = ImageFont.truetype(str(path), size)
    except Exception as e:
        if key == "fredoka":
            raise
        print(f"[font {key}] {e} -> Fredoka", file=sys.stderr)
        return get_font("fredoka", size)
    if spec.get("axes"):
        try:
            f.set_variation_by_axes(spec["axes"])
        except Exception:
            pass
    _fc[k] = f
    return f


# ---------- стили: медиум + свет + палитра (в промпт) и цвета оформления (в компоновку) ----------
STYLES = {
    "papercraft": dict(
        medium="Layered papercraft diorama made of hand-cut paper shapes, soft drop shadows between the layers, visible paper fibers and tiny handmade imperfections.",
        light="Soft diffused studio light from the upper left.",
        palette="Color palette: background #F7E6D5, main shapes #4F7A8C, accents #E8956B, small highlights #F3C969 and #8FB8A8.",
        ink="#2F4F5F", plate="#FFF6EA", accent="#E8956B", fonts=["lilita", "fredoka"]),
    "riso": dict(
        medium="Two-color risograph print with visible halftone dots and slight ink misregistration on warm off-white recycled paper, flat graphic shapes.",
        light="Even flat print look, no lighting effects.",
        palette="Color palette: coral #F26B5B and deep blue #2A4D9B on cream #F5EBDD, overlapping areas in dark plum.",
        ink="#2A4D9B", plate="#F5EBDD", accent="#F26B5B", fonts=["archivo", "bebas"]),
    "gouache": dict(
        medium="Soft gouache children's picture-book illustration with visible brush strokes, chalky texture and rounded friendly shapes.",
        light="Warm late-afternoon light with gentle long shadows.",
        palette="Color palette: cream background #FBF1E1, sage green #A9C5A0, terracotta #D98B6A, butter yellow #F2D7A0, dusty blue #7FA6BF.",
        ink="#4B3B36", plate="#FFF7EA", accent="#D98B6A", fonts=["sniglet", "fredoka"]),
    "clay3d": dict(
        medium="Cute 3D clay render with smooth matte plasticine surfaces, chunky rounded shapes and shallow depth of field.",
        light="Soft studio light from the upper left with gentle ambient occlusion and a faint glow.",
        palette="Color palette: background #F4D9CC, teal #7FB7BE, coral #F2A488, warm yellow #FFE08A.",
        ink="#2E5A66", plate="#FFF4EC", accent="#F2A488", fonts=["fredoka", "poppins"]),
    "geometric": dict(
        medium="Bold flat geometric illustration built from circles, arcs and rectangles in mid-century poster style, crisp edges with a subtle grain overlay.",
        light="Flat color blocking, no shadows.",
        palette="Color palette: sand background #EFE3CF, deep teal #1F4E5F, orange #E76F51, amber #F4A261, green #2A9D8F.",
        ink="#1F4E5F", plate="#F8EFDD", accent="#E76F51", fonts=["bebas", "archivo"]),
    "watercolor": dict(
        medium="Loose watercolor wash illustration with fine ink outlines, soft bleeding edges and visible cold-press paper texture.",
        light="Bright airy morning light.",
        palette="Color palette: paper background #FAF3EA, washes of #9CC5C9, #F2B5A0 and #F6D68A, ink lines #35545C.",
        ink="#35545C", plate="#FFF9F0", accent="#F2B5A0", fonts=["caveat", "dmserif"]),
    "night": dict(
        medium="Hand-painted background-art style illustration with lush soft brushwork and a cozy atmosphere.",
        light="Warm lamp light glowing against a cool blue evening.",
        palette="Color palette: deep navy #22344A, blue #3F6E85, warm lamp glow #FFC978, coral #E98F6E.",
        ink="#FFF1DC", plate="#22344A", accent="#E98F6E", fonts=["dmserif", "poppins"]),
    "collage": dict(
        medium="Mixed-media paper collage with torn paper edges, cut-out shapes, strips of tape and a subtle halftone texture.",
        light="Flat even light, thin paper shadows.",
        palette="Color palette: background #F2E8DA, red-orange #E76F51, teal #2A9D8F, yellow #F4D35E, dark blue #264653.",
        ink="#264653", plate="#FFF4DD", accent="#E76F51", fonts=["archivo", "lilita"]),
    "lineart": dict(
        medium="Minimal continuous line illustration in dark navy ink with a single coral spot color fill, generous white space and fine paper grain.",
        light="Flat, no lighting effects.",
        palette="Color palette: paper #FBF5EC, ink line #1E3A4C, single coral spot color #EE7B5F.",
        ink="#1E3A4C", plate="#FFFAF2", accent="#EE7B5F", fonts=["dmserif", "poppins"]),
    "hills": dict(
        medium="Serene minimal landscape built from layered flat vector hills with a subtle grain and atmospheric perspective.",
        light="Low golden sun glow on the horizon.",
        palette="Color palette: sky gradient #F9D5B5 to #F5A98A, hills #5C8A8E, #3F6570 and #2B4A57, sun #FFE7A8.",
        ink="#2B4A57", plate="#FFF3E4", accent="#F5A98A", fonts=["poppins", "fredoka"]),
}
STYLE_ORDER = ["papercraft", "night", "riso", "clay3d", "watercolor", "geometric", "gouache",
               "collage", "lineart", "hills"]
LAYOUTS = ["plate_top", "bare_top", "banner_bottom", "labels_top", "plate_bottom"]
ZONE = {"plate_top": "top", "bare_top": "top", "labels_top": "top",
        "banner_bottom": "bottom", "plate_bottom": "bottom"}

COMP = {
    "top": "Vertical poster composition: the main subject sits in the lower two thirds of the frame, and the top third is a calm, quiet area of plain background color.",
    "bottom": "Vertical poster composition: the main subject sits in the upper two thirds of the frame, and the bottom third is a calm, quiet area of plain background color.",
}


def build_prompt(scene, style, zone):
    """Проза, предмет первым, только позитивные формулировки (klein не понимает отрицаний)."""
    return f"{scene.strip().rstrip('.')}. {style['medium']} {style['light']} {style['palette']} {COMP[zone]}"


def pick_style_layout(n, row):
    skey = (row.get("style") or "").strip() or STYLE_ORDER[(n - 1) % len(STYLE_ORDER)]
    if skey not in STYLES:
        skey = STYLE_ORDER[(n - 1) % len(STYLE_ORDER)]
    lkey = (row.get("layout") or "").strip()
    if lkey not in LAYOUTS:
        lkey = LAYOUTS[((n - 1) + (n - 1) // len(STYLE_ORDER)) % len(LAYOUTS)]
    return skey, lkey


# ---------- оформление ----------
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def fit(draw, text, fkey, max_w, max_lines=3, start=104, min_size=58):
    if FONTS.get(fkey, {}).get("upper"):
        text = text.upper()
    size = start
    while True:
        fnt = get_font(fkey, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines or size <= min_size:
            return fnt, lines, size
        size -= 4


def draw_lines(d, lines, fnt, cx, top, lh, fill, anchor="mm"):
    y = top + lh / 2
    for ln in lines:
        d.text((cx, y), ln, font=fnt, fill=fill, anchor=anchor)
        y += lh


def badge(img, style, corner, zone):
    """Стикер FOCUS: цвет из стиля, угол — противоположный зоне заголовка."""
    acc = hex2rgb(style["accent"])
    txt = (255, 255, 255) if lum(acc) < 175 else hex2rgb(style["ink"] if lum(hex2rgb(style["ink"])) < 120 else "#2B2B2B")
    bw, bh = 300, 110
    b = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle((24, 26, bw + 24, bh + 26), radius=40, fill=(0, 0, 0, 55))      # мягкая тень
    b = b.filter(ImageFilter.GaussianBlur(5))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle((16, 14, bw + 16, bh + 14), radius=40, fill=acc)
    bd.text(((bw + 32) // 2, (bh + 28) // 2), "FOCUS", font=get_font("fredoka", 72), fill=txt, anchor="mm")
    b = b.rotate(6 if corner.endswith("right") else -6, expand=True, resample=Image.BICUBIC)
    x = W - b.width - 20 if corner.endswith("right") else 20
    y = H - b.height - 20 if corner.startswith("bottom") else 20
    img.paste(b, (x, y), b)


def compose(illustration_path, title, out_path, skey, lkey, fkey, corner):
    st = STYLES[skey]
    ink, plate, acc = hex2rgb(st["ink"]), hex2rgb(st["plate"]), hex2rgb(st["accent"])
    img = Image.open(illustration_path).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    zone = ZONE[lkey]
    max_w = W - 200

    if lkey in ("plate_top", "plate_bottom"):
        fnt, lines, size = fit(d, title, fkey, max_w)
        lh = int(size * 1.18)
        ph = lh * len(lines) + 64
        y0 = 60 if zone == "top" else H - 60 - ph
        d.rounded_rectangle((50, y0, W - 50, y0 + ph), radius=64, fill=plate + (240,), outline=acc, width=6)
        draw_lines(d, lines, fnt, W // 2, y0 + 32, lh, ink)

    elif lkey == "bare_top":
        fnt, lines, size = fit(d, title, fkey, W - 140, start=112)
        lh = int(size * 1.15)
        region = img.crop((0, 40, W, 40 + lh * len(lines) + 60))
        light_bg = lum(ImageStat.Stat(region).mean[:3]) > 150
        fill = hex2rgb(st["ink"]) if (light_bg and lum(ink) < 140) else (hex2rgb("#2B2B2B") if light_bg else (255, 248, 236))
        glow = (255, 248, 236, 200) if light_bg else (20, 30, 40, 170)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        draw_lines(ld, lines, fnt, W // 2 + 3, 75 + 5, lh, glow)
        layer = layer.filter(ImageFilter.GaussianBlur(9))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")
        draw_lines(d, lines, fnt, W // 2, 75, lh, fill)

    elif lkey == "labels_top":
        fnt, lines, size = fit(d, title, fkey, W - 220, start=96)
        lh = int(size * 1.32)
        y = 70
        for i, ln in enumerate(lines):
            tw = d.textlength(ln, font=fnt)
            x0 = 60 + (i % 2) * 46
            d.rounded_rectangle((x0, y, x0 + tw + 64, y + lh), radius=int(lh * 0.36),
                                fill=plate + (245,), outline=acc, width=5)
            d.text((x0 + 32, y + lh / 2), ln, font=fnt, fill=ink, anchor="lm")
            y += lh + 14

    elif lkey == "banner_bottom":
        fnt, lines, size = fit(d, title, fkey, W - 160, max_lines=2, start=100)
        lh = int(size * 1.2)
        bh = lh * len(lines) + 90
        y0 = H - bh
        d.rectangle((0, y0, W, H), fill=ink + (245,))
        d.rectangle((0, y0, W, y0 + 10), fill=acc + (255,))
        draw_lines(d, lines, fnt, W // 2, y0 + 45, lh, plate)

    badge(img, st, corner, zone)
    img.convert("RGB").save(out_path, "JPEG", quality=90, optimize=True)


# ---------- источники картинок ----------
class QuotaError(Exception):
    """Дневной лимит источника исчерпан — повторять бессмысленно."""


def gen_cloudflare(prompt, dest):
    acc, tok = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acc and tok):
        raise QuotaError("CF_ACCOUNT_ID / CF_API_TOKEN не заданы — Cloudflare пропущен")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{CF_MODEL}"
    fields = {"prompt": (None, prompt), "width": (None, str(GEN_W)), "height": (None, str(GEN_H))}
    if CF_GUIDANCE:
        fields["guidance"] = (None, CF_GUIDANCE)
    last = None
    for attempt in range(3):
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {tok}"}, files=fields, timeout=180)
        except requests.RequestException as e:
            last = e
            print(f"cloudflare attempt {attempt + 1}: сеть: {e}", file=sys.stderr)
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code != 200:
            body = r.text[:300]
            low = body.lower()
            if r.status_code == 429 or "neurons" in low or "daily free allocation" in low:
                raise QuotaError(f"Cloudflare: лимит ({r.status_code}): {body}")
            if r.status_code >= 500:
                last = RuntimeError(f"HTTP {r.status_code}: {body}")
                print(f"cloudflare attempt {attempt + 1}: {last}", file=sys.stderr)
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"Cloudflare HTTP {r.status_code}: {body}")
        if r.headers.get("content-type", "").startswith("image/"):
            data = r.content
        else:
            j = r.json()
            res = j.get("result", j)
            b64 = res.get("image") if isinstance(res, dict) else res
            if not b64:
                raise RuntimeError(f"Cloudflare: нет image в ответе: {str(j)[:300]}")
            data = base64.b64decode(b64)
        Image.open(io.BytesIO(data)).convert("RGB").save(dest, "PNG")
        return
    raise RuntimeError(f"Cloudflare недоступен: {last}")


def gen_hf(prompt, dest):
    """Один запрос без повторов: у бесплатного HF ~3 запуска в сутки, неудачные тоже тратятся."""
    from gradio_client import Client
    tok = os.environ.get("HF_TOKEN")
    try:
        client = Client(SPACE, token=tok)
    except TypeError:
        client = Client(SPACE, hf_token=tok)
    try:
        res = client.predict(prompt=prompt, input_images=[], mode_choice="Distilled (4 steps)",
                             seed=0, randomize_seed=True, width=672, height=1008,
                             num_inference_steps=4, guidance_scale=1, prompt_upsampling=False,
                             api_name="/infer")
    except Exception as e:
        if "zerogpu" in str(e).lower() or "quota" in str(e).lower():
            raise QuotaError(f"HF: {e}")
        raise
    first = res[0] if isinstance(res, (list, tuple)) else res
    path = first.get("path") if isinstance(first, dict) else first
    Path(dest).write_bytes(Path(path).read_bytes())


def generate(prompt, dest, state):
    if state["cf_ok"]:
        try:
            gen_cloudflare(prompt, dest)
            return "cloudflare"
        except QuotaError as e:
            print(f"[cloudflare off] {e}", file=sys.stderr)
            state["cf_ok"] = False
        except Exception as e:
            print(f"[cloudflare error] {e}", file=sys.stderr)
    if state["hf_used"] < HF_MAX_PER_RUN:
        state["hf_used"] += 1
        try:
            gen_hf(prompt, dest)
            return "hf"
        except QuotaError as e:
            print(f"[hf off] {e}", file=sys.stderr)
            state["hf_used"] = HF_MAX_PER_RUN
        except Exception as e:
            print(f"[hf error] {e}", file=sys.stderr)
    raise RuntimeError("все источники картинок сейчас недоступны")


# ---------- один пин ----------
def make_pin(n, row, raw, final, state):
    skey, lkey = pick_style_layout(n, row)
    st = STYLES[skey]
    rng = random.Random(n * 9973)
    fkey = rng.choice(st["fonts"])
    zone = ZONE[lkey]
    corner = rng.choice(["bottom-right", "bottom-left"] if zone == "top" else ["top-right", "top-left"])
    src = generate(build_prompt(row["scene_prompt"], st, zone), raw, state)
    compose(raw, row["title"], final, skey, lkey, fkey, corner)
    return src, f"{skey}/{lkey}/{fkey}"


def contact_sheet(paths, out):
    cols, tw, th = 5, 300, 450
    rows_n = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows_n * th), (245, 245, 245))
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(out, "JPEG", quality=88)


# ---------- режимы ----------
def run_test(rows):
    shutil.rmtree("test", ignore_errors=True)
    os.makedirs("test", exist_ok=True)
    state, ok = {"cf_ok": True, "hf_used": 0}, 0
    for i, r in enumerate(rows[:3], 1):
        n = int(r["id"])
        t0 = time.time()
        try:
            src, combo = make_pin(n, r, f"test/{n}_raw.png", f"test/{n}.jpg", state)
            os.remove(f"test/{n}_raw.png")
            print(f"test pin {n}: OK via {src} [{combo}] in {time.time() - t0:.1f}s")
            ok += 1
        except Exception as e:
            print(f"test pin {n}: FAIL {e}", file=sys.stderr)
    if ok == 0:
        sys.exit(1)


def run_demo(rows):
    """По одной картинке на каждый стиль: сравнить художественные направления."""
    shutil.rmtree("test", ignore_errors=True)
    os.makedirs("test", exist_ok=True)
    state, done, paths = {"cf_ok": True, "hf_used": 0}, 0, []
    for i, skey in enumerate(STYLE_ORDER):
        row = dict(rows[i % len(rows)])
        row["style"] = skey
        row["layout"] = LAYOUTS[i % len(LAYOUTS)]
        n = int(row["id"])
        t0 = time.time()
        raw, final = f"test/demo_{i + 1:02d}_{skey}_raw.png", f"test/demo_{i + 1:02d}_{skey}.jpg"
        try:
            src, combo = make_pin(n, row, raw, final, state)
            os.remove(raw)
            print(f"demo {i + 1:02d} {skey}: OK via {src} [{combo}] in {time.time() - t0:.1f}s")
            paths.append(final)
            done += 1
        except Exception as e:
            print(f"demo {i + 1:02d} {skey}: FAIL {e}", file=sys.stderr)
            break
    if paths:
        contact_sheet(paths, "test/contact_sheet.jpg")
    if done == 0:
        sys.exit(1)


def stock_target(rows, now):
    """Сколько картинок нужно иметь готовыми: остаток на сегодня + STOCK_DAYS следующих дней по плану."""
    today = now.date()
    assigned = 0
    for r in rows:
        if P.status(r) in ("scheduled", "published"):
            dt = P.parse_dt(r.get("scheduled_at"))
            if dt and dt.date() == today:
                assigned += 1
    rest_today = max(0, P.pins_for_day(today) - assigned)
    ahead = sum(P.pins_for_day(today + timedelta(days=i)) for i in range(1, P.cfg("STOCK_DAYS") + 1))
    return rest_today + ahead


def main():
    rows, header = P.load_rows("pins.csv")
    if "--test" in sys.argv:
        return run_test(rows)
    if "--demo" in sys.argv:
        return run_demo(rows)
    os.makedirs("images", exist_ok=True)
    now = P.now_kyiv()
    ready = sum(1 for r in rows if P.status(r) == "ready")
    target = stock_target(rows, now)
    want = int(PINS_PER_RUN) if PINS_PER_RUN else min(max(0, target - ready), GEN_MAX_PER_RUN)
    print(f"Склад: готово {ready}, нужно {target} (на {P.cfg('STOCK_DAYS')} дн. вперёд + остаток сегодня); "
          f"сделать сейчас: {want}")
    state, done = {"cf_ok": True, "hf_used": 0}, 0
    for r in sorted(rows, key=lambda x: int(x["id"])):
        if done >= want:
            break
        if P.status(r) != "new":
            continue
        n = int(r["id"])
        raw, final = f"images/{n}_raw.png", f"images/{n}.jpg"
        try:
            src, combo = make_pin(n, r, raw, final, state)
            os.remove(raw)
            r["status"] = "ready"
            done += 1
            P.save_rows(rows, header, "pins.csv")
            print(f"done {n} via {src} [{combo}]")
        except Exception as e:
            print(f"pin {n} skipped: {e}", file=sys.stderr)
            break
    left_new = sum(1 for r in rows if P.status(r) == "new")
    runway = ready + done + left_new
    week = sum(P.pins_for_day(now.date() + timedelta(days=i)) for i in range(1, 8))
    if runway < week:
        print(f"::warning::В pins.csv осталось {runway} пинов (готовых + новых) — меньше, чем нужно на неделю ({week}). "
              f"Пора добавить строки.")
    if done < want:
        print(f"::warning::Сделано {done} из {want} картинок (источники исчерпаны или строки new закончились)")
    if want > 0 and done == 0 and left_new > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
