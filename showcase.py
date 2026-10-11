"""FOCUS showcase: «витринные» картинки из РЕАЛЬНЫХ страниц планера, стикеров и экранов HTML-планера.

Нейросеть не используется (ИИ плохо рисует интерфейс и мелкий текст), поэтому квоту Cloudflare не тратит.
Запуск:  python showcase.py            -> images/social/showcase/*.jpg  (Facebook 1080x1350, X 1600x900)
         python showcase.py fb_restart -> только одна картинка
Материалы лежат в assets/showcase/ (pages, stickers, screens, logo); шрифты Lora и Nunito — в fonts/.
Правила: без цен и ссылок на картинке (цена может измениться), 3-6 слов крупно, один ясный образ.
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

A = Path("assets/showcase")
OUT = Path("images/social/showcase")

INK = (31, 26, 29)
CREAM = (241, 232, 214)
CREAM_DARK = (231, 220, 196)
GOLD = (230, 193, 90)
SAGE = (157, 176, 138)
TEAL = (122, 158, 160)
CORAL = (201, 127, 122)
NIGHT = (22, 21, 28)
TEXT_LIGHT = (250, 244, 232)


def font(name, size, wght=700):
    f = ImageFont.truetype(f"fonts/{name}.ttf", size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_text(d, text, max_w, max_lines, start, min_size=56, name="Lora", wght=700):
    size = start
    while True:
        f = font(name, size, wght)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines or size <= min_size:
            return f, lines, size
        size -= 4


def background(w, h, base, dots=True, seed=1):
    img = Image.new("RGB", (w, h), base)
    if dots:
        d = ImageDraw.Draw(img, "RGBA")
        step = 54
        shade = (0, 0, 0, 16) if sum(base) > 450 else (255, 255, 255, 14)
        for y in range(step // 2, h, step):
            for x in range(step // 2, w, step):
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=shade)
    return img


def blob(img, cx, cy, r, color, alpha=60):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))


def card(src, width, angle=0, radius=30, border=6, shadow=14, outline=INK, shadow_color=INK):
    """Страница/экран в фирменной рамке планера: жирный контур + жёсткая смещённая тень, с поворотом."""
    im = Image.open(src).convert("RGB")
    h = int(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    pad = border + shadow + 6
    base = Image.new("RGBA", (width + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((pad + shadow, pad + shadow, pad + shadow + width, pad + shadow + h), radius=radius,
                        fill=shadow_color + (255,))
    mask = Image.new("L", (width, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, h - 1), radius=radius - border // 2, fill=255)
    d.rounded_rectangle((pad - border, pad - border, pad + width + border, pad + h + border),
                        radius=radius + border // 2, fill=outline + (255,))
    base.paste(im, (pad, pad), mask)
    return base.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else base


def phone(src, width, angle=0, bezel=16, radius=64):
    im = Image.open(src).convert("RGB")
    h = int(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    pad = bezel + 24
    base = Image.new("RGBA", (width + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad - bezel + 10, pad - bezel + 18, pad + width + bezel + 10,
                                         pad + h + bezel + 18), radius=radius + bezel, fill=(0, 0, 0, 120))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((pad - bezel, pad - bezel, pad + width + bezel, pad + h + bezel), radius=radius + bezel,
                        fill=(10, 10, 14, 255), outline=GOLD + (255,), width=4)
    mask = Image.new("L", (width, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, h - 1), radius=radius, fill=255)
    base.paste(im, (pad, pad), mask)
    return base.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else base


def sticker(name, height, angle=0, shadow=True):
    im = Image.open(A / "stickers" / f"{name}.png").convert("RGBA")
    w = int(im.width * height / im.height)
    im = im.resize((w, height), Image.LANCZOS)
    return im.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else im


def put(img, layer, cx, cy):
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)


def logo_chip(img, x, y, width=230, radius=20, border=4):
    lg = Image.open(A / "logo" / "focus_logo.jpg").convert("RGB")
    # логотип 1440x576: берём центральную часть с буквой F и словом FOCUS (без подписи-слогана по краям)
    lg = lg.crop((330, 60, 1110, 470))
    h = int(lg.height * width / lg.width)
    lg = lg.resize((width, h), Image.LANCZOS)
    m = Image.new("L", lg.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, lg.width - 1, lg.height - 1), radius=radius, fill=255)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - border, y - border, x + lg.width + border, y + lg.height + border), radius=radius + border,
                        outline=GOLD, width=border)
    img.paste(lg, (x, y), m)
    return lg.height


def headline(img, text, box, color=INK, start=104, max_lines=3, align="center", name="Lora", wght=700, hl=None):
    """Крупный заголовок в рамке box=(x0,y0,x1,y1). hl — слово, под которым рисуется золотой «маркер»."""
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    if "\n" in text:                      # ручные переносы: подбираем размер под самую длинную строку
        size = start
        while True:
            f = font(name, size, wght)
            lines = text.split("\n")
            if max(d.textlength(ln, font=f) for ln in lines) <= x1 - x0 or size <= 56:
                break
            size -= 4
    else:
        f, lines, size = fit_text(d, text, x1 - x0, max_lines, start, name=name, wght=wght)
    lh = int(size * 1.16)
    total = lh * len(lines)
    y = y0 + (y1 - y0 - total) // 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = x0 + ((x1 - x0) - tw) / 2 if align == "center" else x0
        if hl and hl in ln:
            pre = ln.split(hl)[0]
            hx = x + d.textlength(pre, font=f)
            hw = d.textlength(hl, font=f)
            d.rounded_rectangle((hx - 10, y + int(size * 0.58), hx + hw + 10, y + int(size * 1.02)), radius=14,
                                fill=GOLD + (170,))
        d.text((x, y), ln, font=f, fill=color)
        y += lh
    return total


def strip(img, text, y, h, color=INK, fg=TEXT_LIGHT, x0=40, x1=None, logo=False):
    """Нижняя плашка с подписью продукта (логотип FOCUS слева внутри плашки)."""
    w = img.width
    x1 = x1 or (w - 40)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((x0, y, x1, y + h), radius=h // 2, fill=color + (255,))
    f = font("Nunito", int(h * 0.34), 800)
    left = x0
    if logo:
        lh = logo_chip(img, x0 + 14, y + 12, 128, radius=14, border=3)
        left = x0 + 160
    d.text(((left + x1) / 2, y + h / 2), text, font=f, fill=fg, anchor="mm")


# ------------------------------------------------------------------ Facebook 1080x1350 (4:5)
def fb_restart():
    img = background(1080, 1350, CREAM)
    blob(img, 160, 380, 260, SAGE, 70)
    blob(img, 960, 1000, 300, GOLD, 80)
    headline(img, "Missed a week?\nRestart softly.", (60, 50, 1020, 330), start=112, hl="Restart")
    put(img, card(A / "pages/restart.png", 560, -4), 400, 760)
    put(img, sticker("forgive-gap", 112, 6), 840, 470)
    put(img, sticker("start-small", 112, -5), 880, 640)
    put(img, sticker("micro-step", 112, 4), 850, 810)
    put(img, sticker("youre-fine", 104, -7), 870, 980)
    strip(img, "Soft Structure Premium  ·  fillable ADHD planner", 1204, 100, logo=True)
    return img


def fb_dopamine():
    img = background(1080, 1350, (247, 239, 224))
    blob(img, 900, 330, 260, CORAL, 55)
    blob(img, 130, 1050, 300, TEAL, 60)
    headline(img, "Pre-decide\nyour rewards.", (60, 50, 1020, 330), start=116, hl="rewards")
    put(img, card(A / "pages/dopamine.png", 560, 4), 670, 760)
    put(img, sticker("dopamine-hit", 112, -6), 230, 520)
    put(img, sticker("self-care", 112, 5), 205, 700)
    put(img, sticker("body-double", 112, -4), 230, 880)
    put(img, sticker("battery-full", 104, 6), 210, 1050)
    strip(img, "Dopamine Menu  ·  inside Soft Structure Premium", 1204, 100, logo=True)
    return img


def fb_phone():
    img = background(1080, 1350, NIGHT)
    blob(img, 200, 300, 280, (122, 88, 180), 70)
    blob(img, 900, 1050, 320, GOLD, 50)
    headline(img, "One task.\nZero guilt.", (60, 50, 1020, 320), color=TEXT_LIGHT, start=124, hl="Zero guilt.")
    put(img, phone(A / "screens/phone1.png", 400, -5), 330, 775)
    put(img, phone(A / "screens/phone2.png", 400, 4), 740, 840)
    strip(img, "FOCUS HTML planner  ·  works offline  ·  no account", 1204, 100, color=GOLD, fg=INK)
    return img


# ------------------------------------------------------------------ X 1600x900 (16:9)
def x_decision():
    img = background(1600, 900, CREAM)
    blob(img, 1250, 150, 300, SAGE, 70)
    blob(img, 160, 800, 260, GOLD, 80)
    headline(img, "Too many decisions?\nPull a ticket.", (80, 110, 860, 600), align="left", start=96, max_lines=4,
             hl="ticket.")
    d = ImageDraw.Draw(img)
    d.text((86, 650), "Decision Menu from the FOCUS planner", font=font("Nunito", 36, 700), fill=(92, 84, 78))
    put(img, card(A / "pages/decision.png", 500, 5), 1180, 450)
    put(img, sticker("safe-to-stop", 96, -6), 940, 250)
    put(img, sticker("one-step", 96, 5), 1420, 690)
    logo_chip(img, 86, 740, 190)
    return img


def x_stickers():
    img = background(1600, 900, (247, 239, 224))
    blob(img, 1300, 760, 300, CORAL, 55)
    blob(img, 150, 150, 240, TEAL, 60)
    headline(img, "120+ stickers\nfor ADHD brains", (80, 110, 800, 600), align="left", start=100, max_lines=4,
             hl="stickers")
    d = ImageDraw.Draw(img)
    d.text((86, 650), "Transparent PNG, ready for GoodNotes", font=font("Nunito", 36, 700), fill=(92, 84, 78))
    names = ["high-energy", "low-energy", "battery-full", "calm", "done-enough", "restart", "micro-step",
             "overwhelm", "hyperfocus", "body-double", "dopamine-hit", "self-care", "priority-1", "pause",
             "youre-fine", "one-step", "enough-for-today", "forgive-gap", "start-small", "safe-to-stop"]
    rng = random.Random(7)
    cols = [980, 1300]
    y = 90
    i = 0
    while y < 840 and i < len(names):
        for cx in cols:
            if i >= len(names):
                break
            put(img, sticker(names[i], 84, rng.choice([-6, -3, 3, 6])), cx + rng.randint(-30, 30), y)
            i += 1
        y += 104
    logo_chip(img, 86, 740, 190)
    return img


def x_desktop():
    img = background(1600, 900, NIGHT)
    blob(img, 1280, 450, 360, (122, 88, 180), 70)
    blob(img, 120, 820, 280, GOLD, 40)
    headline(img, "Start tiny.\nStart now.", (80, 110, 860, 600), color=TEXT_LIGHT, align="left", start=116,
             max_lines=3, hl="Start now.")
    d = ImageDraw.Draw(img)
    d.text((86, 650), "A kind timer. No countdown pressure.", font=font("Nunito", 36, 700), fill=(222, 214, 200))
    put(img, card(A / "screens/desktop_timer.png", 560, 3, outline=GOLD, shadow_color=(10, 10, 14)), 1210, 450)
    logo_chip(img, 86, 740, 190)
    return img


JOBS = {
    "fb_restart": (fb_restart, "fb-showcase-restart"),
    "fb_dopamine": (fb_dopamine, "fb-showcase-dopamine"),
    "fb_phone": (fb_phone, "fb-showcase-planner-phone"),
    "x_decision": (x_decision, "x-showcase-decision"),
    "x_stickers": (x_stickers, "x-showcase-stickers"),
    "x_desktop": (x_desktop, "x-showcase-desktop"),
}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    keys = argv or list(JOBS)
    for k in keys:
        fn, name = JOBS[k]
        im = fn().convert("RGB")
        p = OUT / f"{name}.jpg"
        im.save(p, "JPEG", quality=92, optimize=True)
        print("OK", p, im.size)


if __name__ == "__main__":
    main(sys.argv[1:])
