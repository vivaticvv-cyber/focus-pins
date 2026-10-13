"""Продуктовые пины Pinterest 1000x1500 из РЕАЛЬНЫХ страниц планера, стикеров и экранов HTML-планера (без нейросети).

Запуск:  python pinterest_product.py            -> images/N.jpg для всех пинов из SPECS (N = id строки pins.csv)
         python pinterest_product.py 60 104     -> только указанные id
         python pinterest_product.py --demo     -> images/pins_product_demo/ (все по порядку + contact_sheet.jpg)
Раскладки: page_stickers (страница + стикеры), duo_pages (две страницы), fan3 (веер из трёх), closeup (крупный план
страницы), phone_duo / phone_solo (экраны HTML-планера), screen (экран ПК), sticker_wall (стена стикеров), bundle.
Цен и ссылок на картинке нет. Шрифты Lora и Nunito лежат в fonts/, материалы в assets/showcase/.
"""
import io
import pathlib
import random
import sys

from PIL import Image, ImageDraw

import showcase as S

W, H = 1000, 1500
PAGES = S.A / "pages"
SCREENS = S.A / "screens"

PALETTES = {
    "cream": dict(bg=S.CREAM, ink=S.INK, dots=True, blobs=[(140, 420, 260, S.SAGE, 70), (900, 1050, 300, S.GOLD, 80)]),
    "mint": dict(bg=(231, 237, 223), ink=S.INK, dots=True, blobs=[(860, 380, 280, S.TEAL, 60), (120, 1100, 300, S.GOLD, 70)]),
    "blush": dict(bg=(247, 232, 224), ink=S.INK, dots=True, blobs=[(880, 400, 260, S.CORAL, 55), (130, 1120, 300, S.SAGE, 60)]),
    "night": dict(bg=S.NIGHT, ink=S.TEXT_LIGHT, dots=False, blobs=[(200, 380, 300, (122, 88, 180), 70), (860, 1150, 320, S.GOLD, 50)]),
}
FMT_PDF = "Fillable  ·  undated  ·  GoodNotes + print"
FMT_TRIAL = "Free 7-day trial  ·  no signup"
FMT_STICK = "120+ transparent PNG stickers"
FMT_BUNDLE = "Fillable PDF + HTML planner  ·  pay once"
FMT_HTML = "FOCUS HTML planner  ·  offline  ·  no account"
STRIP_PDF = "Soft Structure Premium"
STRIP_HTML = "FOCUS  ·  One task. Zero guilt."
STRIP_BUNDLE = "FOCUS Premium Complete Pack"


def crop_file(path, box):
    """Часть изображения (доли 0..1: left, top, right, bottom) как файлоподобный объект для S.card / S.phone."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    b = io.BytesIO()
    c.save(b, "PNG")
    b.seek(0)
    return b


def label(img, text, y, dark):
    d = ImageDraw.Draw(img, "RGBA")
    f = S.font("Nunito", 38, 800)
    tw = d.textlength(text, font=f)
    fill, fg = (S.GOLD, S.INK) if dark else (S.INK, S.TEXT_LIGHT)
    d.rounded_rectangle((W / 2 - tw / 2 - 36, y, W / 2 + tw / 2 + 36, y + 84), radius=42, fill=fill + (255,))
    d.text((W / 2, y + 42), text, font=f, fill=fg, anchor="mm")


def pills(img, items, cx, y0, step=120):
    d = ImageDraw.Draw(img, "RGBA")
    f = S.font("Nunito", 36, 800)
    for i, t in enumerate(items):
        tw = d.textlength(t, font=f)
        y = y0 + i * step
        d.rounded_rectangle((cx - tw / 2 - 26, y + 8, cx + tw / 2 + 42, y + 84), radius=38, fill=(0, 0, 0, 120))
        d.rounded_rectangle((cx - tw / 2 - 34, y, cx + tw / 2 + 34, y + 76), radius=38, fill=S.GOLD + (255,),
                            outline=S.INK, width=4)
        d.text((cx, y + 38), t, font=f, fill=S.INK, anchor="mm")


def frame(pal, headline):
    p = PALETTES[pal]
    img = S.background(W, H, p["bg"], p["dots"])
    for b in p["blobs"]:
        S.blob(img, *b)
    S.headline(img, headline, (50, 40, 950, 320), color=p["ink"], start=96, hl=headline.replace("\n", " ").split()[0])
    return img, pal == "night"


def finish(img, s, dark):
    label(img, s["fmt"], 1262, dark)
    if dark:
        S.strip(img, s["strip"], 1366, 96, color=S.GOLD, fg=S.INK, x0=60, x1=940)
    else:
        S.strip(img, s["strip"], 1366, 96, logo=True, x0=60, x1=940)
    return img


# ------------------------------------------------------------------ раскладки
def page_stickers(s):
    img, dark = frame(s["pal"], s["headline"])
    left = s.get("side", "right") == "right"
    S.put(img, S.card(PAGES / f"{s['page']}.png", 560, -3 if left else 3), 420 if left else 590, 810)
    xs = 810 if left else 190
    for i, (n, a) in enumerate(zip(s["stickers"], (6, -5, 4))):
        S.put(img, S.sticker(n, 104, a), xs + (i % 2) * 20, 540 + i * 170)
    return finish(img, s, dark)


def duo_pages(s):
    img, dark = frame(s["pal"], s["headline"])
    S.put(img, S.card(PAGES / f"{s['pages'][0]}.png", 470, -6), 360, 790)
    S.put(img, S.card(PAGES / f"{s['pages'][1]}.png", 470, 5), 640, 850)
    if s.get("stickers"):
        S.put(img, S.sticker(s["stickers"][0], 100, 6), 800, 520)
        S.put(img, S.sticker(s["stickers"][1], 100, -5), 190, 1100)
    return finish(img, s, dark)


def fan3(s):
    img, dark = frame(s["pal"], s["headline"])
    for pg, ang, cx, cy in zip(s["pages"], (-11, 0, 11), (300, 500, 710), (850, 800, 860)):
        S.put(img, S.card(PAGES / f"{pg}.png", 420, ang), cx, cy)
    return finish(img, s, dark)


def closeup(s):
    img, dark = frame(s["pal"], s["headline"])
    S.put(img, S.card(crop_file(PAGES / f"{s['page']}.png", s["box"]), 780, 0, radius=36), 500, 790)
    S.put(img, S.sticker(s["stickers"][0], 108, 6), 800, 470)
    S.put(img, S.sticker(s["stickers"][1], 108, -5), 210, 1130)
    return finish(img, s, dark)


def phone_duo(s):
    img, dark = frame(s["pal"], s["headline"])
    S.put(img, S.phone(SCREENS / "phone1.png", 380, -5), 320, 830)
    S.put(img, S.phone(SCREENS / "phone2.png", 380, 4), 700, 890)
    return finish(img, s, dark)


def phone_solo(s):
    img, dark = frame(s["pal"], s["headline"])
    src = crop_file(SCREENS / s["screen"], s["box"]) if s.get("box") else SCREENS / s["screen"]
    S.put(img, S.phone(src, 470, -3), 400, 800)
    pills(img, s["pills"], 800, 540)
    return finish(img, s, dark)


def screen(s):
    img, dark = frame(s["pal"], s["headline"])
    S.put(img, S.card(SCREENS / s["screen"], 640, 2, outline=S.GOLD, shadow_color=(10, 10, 14)), 500, 810)
    return finish(img, s, dark)


def sticker_wall(s):
    img, dark = frame(s["pal"], s["headline"])
    rng = random.Random(s["id"])
    names = list(s["stickers"])
    i, y = 0, 400
    while y < 1230:
        for cx in (270, 730):
            n = names[i % len(names)]
            i += 1
            S.put(img, S.sticker(n, 96, rng.choice([-7, -4, 4, 7])), cx + rng.randint(-25, 25), y)
        y += 108
    return finish(img, s, dark)


def bundle(s):
    img, dark = frame(s["pal"], s["headline"])
    S.put(img, S.card(PAGES / "daily.png", 470, -7), 330, 840)
    S.put(img, S.phone(SCREENS / "phone1.png", 360, 5), 700, 860)
    S.put(img, S.sticker("done-enough", 100, -6), 170, 560)
    S.put(img, S.sticker("start-small", 100, 5), 850, 540)
    return finish(img, s, dark)


LAYOUTS = dict(page_stickers=page_stickers, duo_pages=duo_pages, fan3=fan3, closeup=closeup, phone_duo=phone_duo,
               phone_solo=phone_solo, screen=screen, sticker_wall=sticker_wall, bundle=bundle)

WALL = ["high-energy", "low-energy", "battery-full", "calm", "done-enough", "restart", "micro-step", "overwhelm",
        "hyperfocus", "body-double", "dopamine-hit", "self-care", "priority-1", "pause", "youre-fine", "one-step",
        "enough-for-today", "forgive-gap", "start-small", "safe-to-stop"]
WALL2 = ["high-energy", "low-energy", "empty-tank", "battery-full", "calm", "overwhelm", "hyperfocus", "deep-work",
         "creative", "sunlight", "priority-1", "priority-2", "priority-3", "done-enough", "micro-step"]

WALL3 = ["low-energy", "high-energy", "empty-tank", "battery-full", "calm", "overwhelm", "deep-work", "creative",
         "sunlight", "youre-fine", "forgive-gap", "start-small", "safe-to-stop", "pause", "body-double", "self-care"]

SPECS = [
    dict(id=56, layout="phone_duo", pal="night", headline="One Task Planner\nfor ADHD", fmt=FMT_TRIAL, strip=STRIP_HTML),
    dict(id=60, layout="page_stickers", pal="cream", page="quickstart", stickers=["start-small", "one-step", "enough-for-today"],
         headline="5-Minute ADHD\nRoutine Page", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=65, layout="fan3", pal="cream", pages=["daily", "restart", "dopamine"], headline="Digital Planner\nfor GoodNotes",
         fmt="Undated  ·  fillable  ·  A4, A5, Letter", strip=STRIP_PDF),
    dict(id=68, layout="closeup", pal="blush", page="daily", box=(0, 0.04, 1, 0.58), stickers=["micro-step", "done-enough"],
         headline="ADHD Daily Planner\nTop 3 Priorities", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=73, layout="screen", pal="night", screen="desktop_dopamine.png", headline="Wins, Not Streaks\nADHD Planner",
         fmt=FMT_TRIAL, strip=STRIP_HTML),
    dict(id=76, layout="duo_pages", pal="mint", pages=["braindump", "matrix"], stickers=["pause", "one-step"],
         headline="Brain Dump +\nPriority Matrix", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=80, layout="page_stickers", pal="cream", page="decision", stickers=["safe-to-stop", "low-energy", "one-step"],
         side="left", headline="Decision Menu for\nADHD Fatigue", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=84, layout="phone_solo", pal="night", screen="phone1.png", pills=["One task", "A kind timer", "Small wins"],
         headline="Test an ADHD Planner\nfor a Week", fmt=FMT_TRIAL, strip=STRIP_HTML),
    dict(id=88, layout="duo_pages", pal="blush", pages=["weekly", "quickstart"], stickers=["done-enough", "calm"],
         headline="ADHD Weekly Review\nTemplate", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=92, layout="page_stickers", pal="mint", page="restart", stickers=["forgive-gap", "start-small", "micro-step"],
         headline="ADHD Restart\nProtocol Page", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=96, layout="closeup", pal="mint", page="matrix", box=(0, 0.04, 1, 0.62), stickers=["priority-1", "one-step"],
         headline="Priority Matrix\nfor ADHD", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=100, layout="page_stickers", pal="cream", page="mood", stickers=["high-energy", "low-energy", "battery-full"],
         headline="Energy & Mood Log\nPrintable", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=104, layout="page_stickers", pal="blush", page="dopamine", stickers=["dopamine-hit", "self-care", "body-double"],
         side="left", headline="Dopamine Menu\nfor ADHD Brains", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=108, layout="page_stickers", pal="blush", page="selfcare", stickers=["self-care", "calm", "sunlight"],
         headline="ADHD Self-Care\nMenu Printable", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=112, layout="page_stickers", pal="mint", page="hyperfocus", stickers=["hyperfocus", "safe-to-stop", "pause"],
         side="left", headline="Hyperfocus Exit\nPlan for ADHD", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=118, layout="sticker_wall", pal="mint", stickers=WALL2, headline="GoodNotes ADHD\nStickers", fmt=FMT_STICK,
         strip=STRIP_PDF),
    dict(id=124, layout="screen", pal="night", screen="desktop_timer.png", headline="Free ADHD Planner\nTrial", fmt=FMT_TRIAL,
         strip=STRIP_HTML),
    dict(id=128, layout="phone_solo", pal="blush", screen="phone2.png", box=(0, 0.2, 1, 0.78),
         pills=["Thought dump", "Slice it", "One task"], headline="ADHD Thought Dump\nTool", fmt=FMT_HTML,
         strip=STRIP_HTML),
    dict(id=133, layout="sticker_wall", pal="cream", stickers=WALL, headline="120+ ADHD\nPlanner Stickers", fmt=FMT_STICK,
         strip=STRIP_PDF),
    dict(id=136, layout="fan3", pal="mint", pages=["weekly", "daily", "quickstart"], headline="Undated ADHD Planner\nNo Catch-Up",
         fmt="48 pages  ·  A4, A5, Letter", strip=STRIP_PDF),
    dict(id=141, layout="phone_solo", pal="night", screen="phone2.png", box=(0, 0.55, 1, 1),
         pills=["Slice it", "4 small steps", "Done!"], headline="Slice Big Tasks\nInto Small Steps", fmt=FMT_HTML,
         strip=STRIP_HTML),
    dict(id=147, layout="bundle", pal="cream", headline="ADHD Planner Bundle\nPaper + Screen", fmt=FMT_BUNDLE, strip=STRIP_BUNDLE),
    # ---- партия 4 (id 164-208)
    dict(id=164, layout="duo_pages", pal="blush", pages=["weekly", "daily"], stickers=["calm", "done-enough"],
         headline="ADHD Planner\nPrintable Pages", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=168, layout="fan3", pal="mint", pages=["matrix", "decision", "quickstart"],
         headline="Executive Function\nPlanner Pages", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=172, layout="page_stickers", pal="blush", page="braindump", stickers=["pause", "one-step", "calm"],
         side="left", headline="ADHD Brain Dump\nTemplate", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=176, layout="page_stickers", pal="cream", page="weekly", stickers=["done-enough", "calm", "start-small"],
         side="left", headline="Weekly Planner for\nADHD Brains", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=180, layout="phone_solo", pal="blush", screen="phone1.png", box=(0, 0.1, 1, 0.62),
         pills=["Battery check", "Kind timer", "Small wins"], headline="ADHD Planner\nThat Works Offline", fmt=FMT_HTML,
         strip=STRIP_HTML),
    dict(id=184, layout="sticker_wall", pal="blush", stickers=WALL3, headline="ADHD Sticker Pack\nfor GoodNotes", fmt=FMT_STICK,
         strip=STRIP_PDF),
    dict(id=188, layout="closeup", pal="mint", page="mood", box=(0, 0.04, 1, 0.6), stickers=["high-energy", "low-energy"],
         headline="Mood + Energy Tracker\nfor ADHD", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=192, layout="bundle", pal="mint", headline="PDF + HTML ADHD\nPlanner Bundle", fmt=FMT_BUNDLE,
         strip=STRIP_BUNDLE),
    dict(id=196, layout="closeup", pal="cream", page="daily", box=(0, 0.42, 1, 0.98), stickers=["micro-step", "one-step"],
         headline="ADHD Time Blocking\nPlanner Page", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=200, layout="fan3", pal="cream", pages=["quickstart", "weekly", "braindump"],
         headline="ADHD Planner\nfor Students", fmt=FMT_PDF, strip=STRIP_PDF),
    dict(id=204, layout="phone_solo", pal="night", screen="phone1.png", box=(0, 0, 1, 0.5),
         pills=["One task", "Battery check", "Kind timer"], headline="Free ADHD Planner\nNo Signup", fmt=FMT_TRIAL,
         strip=STRIP_HTML),
    dict(id=208, layout="fan3", pal="blush", pages=["daily", "dopamine", "restart"],
         headline="Undated ADHD Planner\nfor the New Year", fmt="Undated  ·  fillable  ·  A4, A5, Letter",
         strip=STRIP_PDF),
]


def render(spec):
    return LAYOUTS[spec["layout"]](spec).convert("RGB")


def main(argv):
    demo = "--demo" in argv
    ids = [int(a) for a in argv if a.isdigit()]
    specs = [s for s in SPECS if not ids or s["id"] in ids]
    out = pathlib.Path("images/pins_product_demo" if demo else "images")
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for s in specs:
        p = out / (f"{s['id']}_{s['layout']}.jpg" if demo else f"{s['id']}.jpg")
        render(s).save(p, "JPEG", quality=92, optimize=True)
        paths.append(p)
        print("OK", p)
    if demo and paths:
        cols, tw, th = 6, 300, 450
        sh = Image.new("RGB", (cols * tw, ((len(paths) + cols - 1) // cols) * th), (255, 255, 255))
        for i, p in enumerate(paths):
            sh.paste(Image.open(p).resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
        sh.save(out / "contact_sheet.jpg", "JPEG", quality=88)


if __name__ == "__main__":
    main(sys.argv[1:])
