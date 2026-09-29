"""FOCUS pins: генерация иллюстраций FLUX.2 klein 4B + наложение заголовка и плашки FOCUS."""
import csv, os, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SPACE = "black-forest-labs/FLUX.2-klein-4B"
PINS_PER_RUN = int(os.environ.get("PINS_PER_RUN", "3"))
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf"
FONT_PATH = Path("Fredoka.ttf")
W, H = 1000, 1500
PEACH, BLUE, CORAL, DARK = "#FBE8DA", "#4F7A8C", "#E8956B", "#D9713F"
STYLE = ("Flat vector illustration, soft rounded shapes, subtle paper grain, soft shadows, "
         "warm peach background #FBE8DA, deep teal-blue #4F7A8C and coral #E8956B accents, "
         "gentle cozy mood, seamless single-color gradient background, no text, no letters, "
         "main subject in the lower two thirds, top third left empty")


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
    # заголовок на сквиркл-подложке сверху
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
    # плашка-стикер FOCUS в правом нижнем углу
    bw, bh = 300, 110
    badge = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle((10, 10, bw + 10, bh + 10), radius=40, fill=CORAL)
    bd.text(((bw + 20) // 2, (bh + 20) // 2), "FOCUS", font=font(72), fill="white", anchor="mm")
    badge = badge.rotate(6, expand=True, resample=Image.BICUBIC)
    img.paste(badge, (W - badge.width - 40, H - badge.height - 40), badge)
    img.save(out_path, "PNG")


def generate(prompt, dest):
    from gradio_client import Client
    tok = os.environ.get("HF_TOKEN")
    try:
        client = Client(SPACE, token=tok)
    except TypeError:
        client = Client(SPACE, hf_token=tok)
    last = None
    for attempt in range(4):
        try:
            res = client.predict(prompt=prompt, input_images=[], mode_choice="Distilled (4 steps)",
                                 seed=0, randomize_seed=True, width=672, height=1008,
                                 num_inference_steps=4, guidance_scale=1, prompt_upsampling=False,
                                 api_name="/infer")
            first = res[0] if isinstance(res, (list, tuple)) else res
            path = first.get("path") if isinstance(first, dict) else first
            Path(dest).write_bytes(Path(path).read_bytes())
            return
        except Exception as e:  # квота/перегрузка Space — ждём и повторяем
            last = e
            print(f"attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(30 * (attempt + 1))
    raise RuntimeError(f"generation failed: {last}")


def main():
    os.makedirs("images", exist_ok=True)
    rows = list(csv.DictReader(open("pins.csv", encoding="utf-8")))
    done = 0
    for r in rows:
        if done >= PINS_PER_RUN:
            break
        if r["status"].strip().lower() != "new":
            continue
        n = r["id"].strip()
        raw, final = f"images/{n}_raw.png", f"images/{n}.png"
        try:
            generate(f'{r["scene_prompt"]}. {STYLE}', raw)
            compose(raw, r["title"], final)
            os.remove(raw)
            r["status"] = "ready"
            done += 1
            print("done", n)
        except Exception as e:
            print(f"pin {n} skipped: {e}", file=sys.stderr)
            break  # скорее всего квота — остановиться до завтра
    with open("pins.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
