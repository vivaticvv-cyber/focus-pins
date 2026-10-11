"""Безопасно добавить новую партию строк (pins_batch_N.csv) в pins.csv, не трогая статусы уже сделанных пинов.

Запуск:  python merge_batch.py          (в GitHub: Actions -> «Merge pins batch» -> Run workflow)
Что делает:
  1) берёт все файлы pins_batch_*.csv в корне репозитория;
  2) пропускает id, которые уже есть в pins.csv (повторный запуск ничего не дублирует);
  3) проверяет новые строки тем же lint, что и publish.py --lint, плюс дубли заголовков и описаний;
  4) если замечаний нет — дописывает строки в конец pins.csv (статусы старых строк не меняются)
     и переносит обработанный файл в папку batches/.
При замечаниях ничего не меняется, список проблем виден в журнале запуска.
"""
import csv
import glob
import os
import shutil
import sys
import tempfile

import publish as P


def main():
    files = sorted(glob.glob("pins_batch_*.csv"))
    if not files:
        print("Файлов pins_batch_*.csv нет — нечего добавлять.")
        return 0
    rows, header = P.load_rows("pins.csv")
    have_ids = {int(r["id"]) for r in rows}
    titles = {(r.get("title") or "").strip().lower() for r in rows}
    descs = {(r.get("description") or "").strip() for r in rows}
    added_total, problems = [], 0
    for fn in files:
        new, _ = P.load_rows(fn)
        fresh = []
        for r in new:
            try:
                rid = int(r["id"])
            except (KeyError, ValueError):
                print(f"{fn}: строка без числового id пропущена: {r}")
                problems += 1
                continue
            if rid in have_ids:
                continue
            t, d = (r.get("title") or "").strip().lower(), (r.get("description") or "").strip()
            if t in titles or d in descs:
                print(f"{fn}: пин {rid} повторяет заголовок или описание уже существующего пина")
                problems += 1
                continue
            titles.add(t); descs.add(d); fresh.append(r)
        if not fresh:
            print(f"{fn}: новых строк нет")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "check.csv")
            P.save_rows(fresh, header, p)
            if P.lint(p, images_dir=os.path.join(tmp, "none")):
                problems += 1
                print(f"{fn}: есть замечания lint — партия не добавлена")
                continue
        for r in fresh:
            rows.append({k: r.get(k, "") for k in header})
            have_ids.add(int(r["id"]))
        added_total.append((fn, len(fresh)))
    if problems:
        print(f"::error::Найдено проблем: {problems}. pins.csv не изменён.")
        return 1
    if not added_total:
        return 0
    P.save_rows(rows, header, "pins.csv")
    os.makedirs("batches", exist_ok=True)
    for fn, n in added_total:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
        print(f"Добавлено {n} строк из {fn}")
    print(f"Теперь в pins.csv {len(rows)} строк.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
