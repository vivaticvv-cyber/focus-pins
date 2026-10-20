"""FOCUS pins v3: разнообразные иллюстрации FLUX.2 klein 4B + разные раскладки заголовков + «склад» на 2–3 дня.

Источники картинок: Cloudflare Workers AI (основной) -> HF Space (резерв, без повторов).
Режимы:
  python generate.py          обычный: докручивает «склад» — держит готовые картинки (status=ready)
                              на STOCK_DAYS дней вперёд по плану publish.py; строки new -> images/N.jpg, status=ready
                              (в складе считаются только ИНФОРМАЦИОННЫЕ пины; продуктовые делает pinterest_product.py)
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
        medium="Two-color risograph print with visible способ.",
        light="Even flat print look, no lighting effects.",
        palette="Color palette: coral #F26B5B and deep blue #2A4D9B on cream #F5EBDD, overlapping areas in dark plum.",
        ink="#2A4D9B", plate="#F5EBDD", accent="#F26B5B", fonts=["archivo", "bebas"]),
}
