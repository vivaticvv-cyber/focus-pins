"""Безопасно добавить новую партию строк (pins_batch_N.csv) в pins.csv, не трогая статусы уже сделанных пинов.

Запуск:  python merge_batch.py
Что делает:
  1) берёт все files pins_batch_*.csv в корне;
  2) пропускает id уже в pins.csv;
  3) авто-дополняет description 20–299 символов до >=300;
  4) lint; успешные партии дописываются независимо (один плохой файл не блокирует остальные);
  5) переносит обработанные в batches/.
"""
import csv
import glob
import os
import shutil
import sys
import tempfile

import publish as P

_PAD = " A small visible step is still progress for an ADHD brain."


def ensure_description_length(row, rid, fn):
    d = (row.get("description") or "").strip()
    if len(d) >= 300:
        return False
    if len(d) < 20:
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
    added_total = []
    file_problems = 0
    for fn in files:
        new, _ = P.load_rows(fn)
        fresh = []
        local_problems = 0
        for r in new:
            try:
                rid = int(r["id"])
            except (KeyError, ValueError):
                print(f"{fn}: строка без числового id пропущена: {r}")
                local_problems += 1
                continue
            if rid in have_ids:
                continue
            ensure_description_length(r, rid, fn)
            t, d = (r.get("title") or "").strip().lower(), (r.get("description") or "").strip()
            if t in titles or d in descs:
                print(f"{fn}: пин {rid} повторяет заголовок или описание уже существующего пина")
                local_problems += 1
                continue
            titles.add(t); descs.add(d); fresh.append(r)
        if not fresh:
            if local_problems == 0:
                print(f"{fn}: новых строк нет")
            else:
                print(f"{fn}: новых валидных строк нет (замечаний: {local_problems})")
                file_problems += 1
            continue
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "check.csv")
            P.save_rows(fresh, header, p)
            if P.lint(p, images_dir="images"):
                print(f"{fn}: есть замечания lint — партия не добавлена")
                file_problems += 1
                continue
        for r in fresh:
            rows.append({k: r.get(k, "") for k in header})
            have_ids.add(int(r["id"]))
        added_total.append((fn, len(fresh)))
    if added_total or patch_files:
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
    if file_problems or prob_patch:
        print(f"::warning::{file_problems + prob_patch} файл(ов) с замечаниями пропущены; успешные партии сохранены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
