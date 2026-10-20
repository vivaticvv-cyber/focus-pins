"""Шаг «Подготовка» workflow Autopilot: всё, что нужно сделать до публикации Facebook/X. Запускается ежедневно без человека.

1) если в корне лежат новые партии (pins_batch_*.csv, pins_patch_*.csv, social_batch_*.csv) — добавляет их в pins.csv / social.csv
   (merge_batch.py и merge_social.py: проверки, без дублей, статусы старых строк не меняются);
2) если включена переменная репозитория RECYCLE=1 — аварийное пополнение свежими версиями (recycle.py);
3) рисует картинки для строк social.csv со status=new (social.py --stock 6).
Логика живёт в Python-файлах, поэтому новые версии можно загружать в корень репозитория без правки workflow.
"""
import glob
import os
import subprocess
import sys


def run(cmd):
    print(f"\n$ {cmd}", flush=True)
    return subprocess.call(cmd, shell=True)


def heal_social():
    """Строки social.csv со status=ready, но без картинки, возвращаем в new, чтобы social.py нарисовал картинку.
    (Иначе публикация упадёт на «не указана картинка».)"""
    try:
        import social as S
        rows = S.load()
        n = 0
        for r in rows:
            if r.get("status") == "ready" and not (r.get("image") or "").strip():
                r["status"] = "new"
                n += 1
        if n:
            S.save(rows)
            print(f"heal_social: {n} строк ready без картинки → new")
    except Exception as e:  # не критично для остального
        print(f"::warning::heal_social: {e}")


def main():
    rc = 0
    heal_social()
    if glob.glob("pins_batch_*.csv") or glob.glob("pins_patch_*.csv"):
        rc |= run("python merge_batch.py")
    if glob.glob("social_batch_*.csv"):
        rc |= run("python merge_social.py")
    if os.environ.get("RECYCLE") == "1":
        rc |= run("python recycle.py")
    rc |= run("python product_pins.py")   # продуктовые пины по product_specs.csv (без нейросети; ошибки не критичны)
    rc |= run("python social.py --stock 6")
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())
