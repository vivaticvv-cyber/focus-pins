"""Безопасно добавить новую партию строк (pins_batch_N.csv) в pins.csv, не трогая статусы уже сделанных пинов.

Запуск:  python merge_batch.py   (в GitHub: Actions -> «Merge pins batch» -> Run workflow, а также шагом «Подготовка» Autopilot)
Файлы pins_patch_N.csv ЗАМЕНЯЮТ существующие строки с теми же id, но только если строка ещё имеет status=new.

Что делает (политика «построчно», БЕЗ автодобивки текста):
  1) берёт все файлы pins_batch_*.csv в корне;
  2) пропускает id, которые уже есть в pins.csv (повторный запуск ничего не дублирует);
  3) каждую строку проверяет тем же lint, что и publish.py --lint, плюс дубли заголовков и описаний;
  4) ХОРОШИЕ строки дописывает в pins.csv, ПЛОХИЕ не теряются: уходят в batches/rejected_<файл>.csv
     с причиной в batches/_report.md; один плохой пин не блокирует остальные;
  5) обработанный файл переносится в batches/.
Текст пинов скрипт НЕ меняет: исправляет автор строки (см. FOCUS-grok-fixes.md).
"""
import contextlib
import csv
import datetime
import glob
import io
import os
import shutil
import sys
import tempfile

import publish as P

REPORT = os.path.join("batches", "_report.md")


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
            issues = row_issues(pr, header)
            if issues:
                print(f"{fn}: id {rid} патч НЕ применён: {'; '.join(issues)}")
                problems += 1
                continue
            for k in header:
                cur[k] = pr.get(k, "")
            done += 1
        used.append(fn)
    return done, problems, used


def shape_issue(row):
    """Проверка формы строки CSV: лишние колонки почти всегда значат запятую без кавычек внутри текста
    (например, в pin_title), из-за чего поля сдвигаются и описание «укорачивается»."""
    if row.get(None):
        return (f"лишних колонок: {len(row[None])}; в одном из полей есть запятая без кавычек "
                f"(заключайте КАЖДОЕ текстовое поле в двойные кавычки)")
    if any(v is None for v in row.values()):
        return "колонок меньше, чем в заголовке: строка оборвана"
    return ""


def row_issues(row, header):
    """Список замечаний lint по одной строке (пустой список = строка годная)."""
    sh = shape_issue(row)
    if sh:
        return [sh]
    if P.status(row) == "new" and ((row.get("scheduled_at") or "").strip() or (row.get("buffer_post_id") or "").strip()):
        return ["у строки status=new заполнены служебные колонки scheduled_at/buffer_post_id "
                "(вероятно, ссылка попала не в колонку link: у новой строки все 13 колонок должны стоять на своих местах)"]
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "one.csv")
        P.save_rows([{k: row.get(k, "") for k in header}], header, p)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bad = P.lint(p, images_dir="images")
    if not bad:
        return []
    lines = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip() and not ln.startswith("Строк:")]
    return lines or ["lint: замечание (см. publish.py --lint)"]


def write_rejected(fn, header, rejected):
    os.makedirs("batches", exist_ok=True)
    out = os.path.join("batches", "rejected_" + os.path.basename(fn))
    P.save_rows([r for r, _ in rejected], header, out)
    return out


def append_report(entries):
    os.makedirs("batches", exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(f"\n## {stamp}\n")
        for line in entries:
            f.write(("" if line.startswith(" ") else "- ") + line + "\n")


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
    added_total, report, n_rejected = [], [], 0
    for fn in files:
        new, _ = P.load_rows(fn)
        fresh, rejected = [], []
        for r in new:
            try:
                rid = int(r["id"])
            except (KeyError, ValueError):
                rejected.append((r, "строка без числового id")
                continue
            if rid in have_ids:
                continue
            issues = row_issues(r, header)
            t, d = (r.get("title") or "").strip().lower(), (r.get("description") or "").strip()
            if t in titles:
                issues.append("title повторяет существующий пин")
            if d in descs:
                issues.append("description повторяет существующий пин")
            if issues:
                rejected.append((r, "; ".join(issues)))
                continue
            titles.add(t); descs.add(d); fresh.append(r)
        for r in fresh:
            rows.append({k: r.get(k, "") for k in header})
            have_ids.add(int(r["id"]))
        if fresh:
            added_total.append((fn, len(fresh))
        if rejected:
            n_rejected += len(rejected)
            out = write_rejected(fn, header, rejected)
            for r, why in rejected:
                print(f"{fn}: пин {r.get('id')} ОТКЛОНЁН: {why}")
            report.append(f"{fn}: принято {len(fresh)}, отклонено {len(rejected)} → {out}")
            report += [f"  - id {r.get('id')}: {why}" for r, why in rejected]
        else:
            report.append(f"{fn}: принято {len(fresh)}, отклонено 0")
        if not fresh and not rejected:
            print(f"{fn}: новых строк нет")
    if added_total or patch_files:
        P.save_rows(rows, header, "pins.csv")
        for fn, n in added_total:
            print(f"Добавлено {n} строк из {fn}")
        if patch_files:
            print(f"Заменено строк патчами: {n_patch}")
        print(f"Теперь в pins.csv {len(rows)} строк.")
    os.makedirs("batches", exist_ok=True)
    for fn in files + patch_files:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
    if patch_files:
        report.append(f"патчи: заменено {n_patch}, не применено {prob_patch}")
    if report:
        append_report(report)
    if n_rejected or prob_patch:
        print(f"::warning::Отклонено строк: {n_rejected + prob_patch}. Остальные приняты. Список — batches/_report.md, строки — batches/rejected_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
