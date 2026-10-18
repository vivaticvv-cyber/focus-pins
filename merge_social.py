"""Безопасно добавить новые строки Facebook/X (social_batch_N.csv) в social.csv, не трогая статусы уже сделанных.

Запуск:  python merge_social.py   (автоматически — шагом «Подготовка» workflow Autopilot)
Что делает:
  1) берёт все файлы social_batch_*.csv в корне репозитория;
  2) пропускает id, которые уже есть в social.csv (повторный запуск ничего не дублирует);
  3) проверяет новые строки тем же lint, что и social.py --lint, плюс дубли текста;
  4) если замечаний нет — дописывает строки в конец social.csv и переносит файл в папку batches/.
При замечаниях ничего не меняется, список проблем виден в журнале запуска.
"""
import csv
import glob
import os
import shutil
import sys

import social as S


def main():
    files = sorted(glob.glob("social_batch_*.csv"))
    if not files:
        print("Файлов social_batch_*.csv нет — нечего добавлять.")
        return 0
    rows = S.load()
    have_ids = {r["id"] for r in rows}
    texts = {(r.get("text") or "").strip() for r in rows}
    problems, added = 0, []
    for fn in files:
        with open(fn, encoding="utf-8-sig", newline="") as f:
            new = [dict(r) for r in csv.DictReader(f)]
        fresh = []
        for r in new:
            if not r.get("id") or r["id"] in have_ids:
                continue
            t = (r.get("text") or "").strip()
            if t in texts:
                print(f"{fn}: строка {r['id']} повторяет текст уже существующей строки")
                problems += 1
                continue
            texts.add(t)
            fresh.append({k: r.get(k, "") for k in S.FIELDS})
        if not fresh:
            print(f"{fn}: новых строк нет")
            continue
        if S.lint(fresh):
            print(f"{fn}: есть замечания lint — партия не добавлена")
            problems += 1
            continue
        rows.extend(fresh)
        have_ids.update(r["id"] for r in fresh)
        added.append((fn, len(fresh)))
    if problems:
        print(f"::error::Найдено проблем: {problems}. social.csv не изменён.")
        return 1
    if not added:
        return 0
    S.save(rows)
    os.makedirs("batches", exist_ok=True)
    for fn, n in added:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
        print(f"Добавлено {n} строк из {fn}")
    print(f"Теперь в social.csv {len(rows)} строк.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
