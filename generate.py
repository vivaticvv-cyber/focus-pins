"""FOCUS pins: иллюстрации FLUX.2 klein 4B + наложение заголовка и плашки FOCUS.

Источники картинок (по порядку):
  1) Cloudflare Workers AI  @cf/black-forest-labs/flux-2-klein-4b  (основной, бесплатный лимит 10 000 нейронов/сутки)
  2) Hugging Face Space FLUX.2-klein-4B (ZeroGPU)                  (резерв, без повторов, не больше HF_MAX_PER_RUN)

Режимы:
  python generate.py          — обычный: берёт строки pins.csv со статусом new, делает картинки в images/, ставит ready
  python generate.py --test   — тест: первые 3 строки pins.csv -> test/ (raw + готовый пин), pins.csv не меняется
"""
import base64, csv, io, os, sys, time, urllib.request
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

SPACE = "black-forest-labs/FLUX.2-klein-4B"
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
PINS_PER_RUN = int(os.environ.get("PINS_PER_RUN", "2"))
HF_MAX_PER_RUN = int(os.environ.get("HF_MAX_PER_RUN", "1"))
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf"
FONT_PATH = Path("Fredoka.ttf")
W, H = 1000, 1500          # финальный размер пина
GEN_W, GEN_H = 1024, 1536  # размер генерации (то же соотношение 2:3)
PEACH, BLUE, CORAL, DARK = "#FBE8DA", "#4F7A8C", "#E8956B", "#D9713F"
STYLE = ("Flat vector illustration, soft rounded shapes, subtle paper grain, soft shadows, "
         "warm peach background #FBE8DA, deep teal-blue #4F7A8C and coral #E8956B accents, "
         "gentle cozy mood, seamless single-color gradient background, no text, no letters, "
         "main subject in the lower two thirds, top third left empty")


class QuotaError(Exception):
    """Дневной лимит источника исчерпан — повторять бессмысленно."""


# ---------- оформление (без изменений) ----------
def font(size):
    if not FONT_PATH.exists():
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    f = ImageFont.truetype(str(FONT_PATH), size)
    try:
        f.set_variation_by_axes([700, 100])  # [вес, ширина]
    except Exception:
        pass
    return f


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def compose(illustration_path, title, out_path):
    img = Image.open(illustration_path).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    size = 92
    while True:
        fnt = font(size)
        lines = wrap(d, title, fnt, W - 200)
        if len(lines) <= 3 or size <= 56:
            break
        size -= 6
    lh = int(size * 1.15)
    plate_h = lh * len(lines) + 70
    d.rounded_rectangle((50, 60, W - 50, 60 + plate_h), radius=70, fill=(251, 232, 218, 235),
                        outline=DARK, width=5)
    y = 60 + 35
    for ln in lines:
        d.text((W // 2, y), ln, font=fnt, fill=BLUE, anchor="mt")
        y += lh
    bw, bh = 300, 110
    badge = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((10, 10, bw + 10, bh + 10), radius=40, fill=CORAL)
    bd.text(((bw + 20) // 2, (bh + 20) // 2), "FOCUS", font=font(72), fill="white", anchor="mm")
    badge = badge.rotate(6, expand=True, resample=Image.BICUBIC)
    img.paste(badge, (W - badge.width - 40, H - badge.height - 40), badge)
    img.save(out_path, "PNG")


# ---------- источники картинок ----------
def gen_cloudflare(prompt, dest):
    acc, tok = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
    if not (acc and tok):
        raise QuotaError("CF_ACCOUNT_ID / CF_API_TOKEN не заданы — Cloudflare пропущен")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{CF_MODEL}"
    fields = {"prompt": (None, prompt), "width": (None, str(GEN_W)), "height": (None, str(GEN_H))}
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
    """Один запрос, без повторов: у бесплатного HF ~3 запуска в сутки, неудачные тоже тратятся."""
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
    """Cloudflare -> HF. Возвращает имя источника или бросает RuntimeError."""
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


# ---------- режимы ----------
def run_test(rows):
    os.makedirs("test", exist_ok=True)
    state = {"cf_ok": True, "hf_used": 0}
    ok = 0
    for r in rows[:3]:
        n = r["id"].strip()
        raw, final = f"test/{n}_raw.png", f"test/{n}.png"
        t0 = time.time()
        try:
            src = generate(f'{r["scene_prompt"]}. {STYLE}', raw, state)
            compose(raw, r["title"], final)
            print(f"test pin {n}: OK via {src} in {time.time() - t0:.1f}s")
            ok += 1
        except Exception as e:
            print(f"test pin {n}: FAIL {e}", file=sys.stderr)
    if ok == 0:
        sys.exit(1)


def main():
    rows = list(csv.DictReader(open("pins.csv", encoding="utf-8")))
    if "--test" in sys.argv:
        return run_test(rows)
    os.makedirs("images", exist_ok=True)
    state = {"cf_ok": True, "hf_used": 0}
    done = 0
    for r in rows:
        if done >= PINS_PER_RUN:
            break
        if r["status"].strip().lower() != "new":
            continue
        n = r["id"].strip()
        raw, final = f"images/{n}_raw.png", f"images/{n}.png"
        try:
            src = generate(f'{r["scene_prompt"]}. {STYLE}', raw, state)
            compose(raw, r["title"], final)
            os.remove(raw)
            r["status"] = "ready"
            done += 1
            print(f"done {n} via {src}")
        except Exception as e:
            print(f"pin {n} skipped: {e}", file=sys.stderr)
            break  # все источники исчерпаны — до следующего запуска
    with open("pins.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    if done == 0 and any(r["status"].strip().lower() == "new" for r in rows):
        sys.exit(1)  # ни одной картинки — пусть прогон будет красным


if __name__ == "__main__":
    main()
