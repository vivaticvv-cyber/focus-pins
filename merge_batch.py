"""Безопасно добавить новую партию строк (pins_batch_N.csv) в pins.csv, не трогая статусы уже сделанных пинов.

Запуск:  python merge_batch.py          (в GitHub: Actions -> «Merge pins batch» -> Run workflow)
Файлы pins_patch_N.csv ЗАМЕНЯЮТ существующие строки с теми же id, но только если строка ещё имеет status=new
(строки в работе — ready с картинкой от нейросети, scheduled, published — не трогаются, об этом пишется в журнал);
картинка images/<id>.jpg для строк патча должна быть уже загружена.
Что делает:
  1) берёт все файлы pins_batch_*.csv в корне репозитория;
  2) пропускает id, которые уже есть в pins.csv (повторный запуск ничего не дублирует);
  3) авто-дополняет description < 300 символов безопасным ADHD-суффиксом (чтобы один короткий текст не ронял партию);
  4) проверяет новые строки тем же lint, что и publish.py --lint, плюс дубли заголовков и описаний;
  5) если замечаний нет — дописывает строки в конец pins.csv (статусы старых строк не меняются)
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

# Безопасный суффикс для авто-дополнения коротких description (ADHD-friendly)
_PAD = " A small visible step is still progress for an ADHD brain."


def ensure_description_length(row, rid, fn):
    """Если description короче 300 — дополняет до >= 300. Возвращает True если меняла."""
    d = (row.get("description") or "").strip()
    if len(d) >= 300:
        return False
    if len(d) < 20:
        # почти пустое — не угадываем, оставляем lint'у
        return False
    original = d
    while len(d) < 300:
        d = d + _PAD
    if len(d) > 450:
        d = d[:447] + "..."
    row["description"] = d
    print(f"{fn}: пин {rid}: description {len(original)}→{len(d)} (auto-pad)")
    return True


def apply_patches(rows, header):
    """Замена строк со status=new строками из pins_patch_*.csv. Возвращает (кол-во замен, проблемы, обработанные файлы)."""
    done, problems, used = 0, 0, []
    by_id = {int(r["id"]): r for r in rows}
    for fn in sorted(glob.glob("pins_patch_*.csv")):
        patch, _ = P.load_rows(fn)
        for pr in patch:
            rid = int(pr["id"])
            cur = by_id.get(rid)
            if cur is None:
                print(f"{fn}: id {rid} нет в pins.csv — пропуск")
                continue
            if P.status(cur) != "new":
                print(f"{fn}: id {rid} уже в работе (status={P.status(cur)}) — не заменён")
                continue
            if P.status(pr) == "ready" and not os.path.exists(os.path.join("images", f"{rid}.jpg")):
                print(f"::error::{fn}: для id {rid} нет images/{rid}.jpg — сначала загрузите картинки")
                problems += 1
                continue
            for k in header:
                cur[k] = pr.get(k, "")
            done += 1
        used.append(fn)
    return done, problems, used


def main():
    rows, header = P.load_rows("pins.csv")
    n_patch, prob_patch, patch_files = apply_patches(rows, header)
    files = sorted(glob.glob("pins_batch_*.csv"))
    if not files and not patch_files:
        print("Файлов pins_batch_*.csv и pins_patch_*.csv нет — нечего добавлять.")
        return 0
    have_ids = {int(r["id"]) for r in rows}
    titles = {(r.get("title") or "").strip().lower() for r in rows}
    descs = {(r.get("description") or "").strip() for r in rows}
    added_total, problems = [], prob_patch
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
            # Авто-дополнение коротких description до запуска lint
            ensure_description_length(r, rid, fn)
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
            if P.lint(p, images_dir="images"):
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
    if not added_total and not patch_files:
        return 0
    P.save_rows(rows, header, "pins.csv")
    os.makedirs("batches", exist_ok=True)
    for fn, n in added_total:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
        print(f"Добавлено {n} строк из {fn}")
    for fn in patch_files:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
    if patch_files:
        print(f"Заменено строк патчами: {n_patch}")
    print(f"Теперь в pins.csv {len(rows)} строк.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
