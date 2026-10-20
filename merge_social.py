"""Безопасно добавить новые строки Facebook/X (social_batch_N.csv) в social.csv, не трогая статусы уже сделанных.

Запуск:  python merge_social.py   (автоматически — шагом «Подготовка» workflow Autopilot)
Что делает (политика «построчно», текст не меняется):
  1) берёт все файлы social_batch_*.csv в корне репозитория;
  2) пропускает id, которые уже есть в social.csv (повторный запуск ничего не дублирует);
  3) каждую строку проверяет тем же lint, что и social.py --lint, плюс дубли текста;
  4) хорошие строки дописывает в social.csv; плохие уходят в batches/rejected_<файл>.csv с причиной в batches/_report.md
     (один плохой пост не блокирует остальные, Autopilot не краснеет);
  5) обработанный файл переносится в batches/.
"""
import contextlib
import csv
import datetime
import glob
import io
import os
import shutil
import sys

import social as S

REPORT = os.path.join("batches", "_report.md")


def row_issues(row):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        bad = S.lint([row])
    if not bad:
        return []
    lines = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip() and not ln.startswith("Строк:")]
    return lines or ["lint: замечание (см. social.py --lint)"]


def main():
    files = sorted(glob.glob("social_batch_*.csv"))
    if not files:
        print("Файлов social_batch_*.csv нет — нечего добавлять.")
        return 0
    rows = S.load()
    have_ids = {r["id"] for r in rows}
    texts = {(r.get("text") or "").strip() for r in rows}
    added, report, n_rejected = [], [], 0
    for fn in files:
        with open(fn, encoding="utf-8-sig", newline="") as f:
            new = [dict(r) for r in csv.DictReader(f)]
        fresh, rejected = [], []
        for r in new:
            if not r.get("id") or r["id"] in have_ids:
                continue
            row = {k: r.get(k, "") for k in S.FIELDS}
            if r.get(None):
                issues = [f"лишних колонок: {len(r[None])}; в тексте запятая без кавычек (заключайте каждое текстовое поле в двойные кавычки)"]
            elif any(v is None for v in r.values()):
                issues = ["колонок меньше, чем в заголовке: строка оборвана"]
            else:
                issues = row_issues(row)
            if (row.get("text") or "").strip() in texts:
                issues.append("text повторяет существующую строку")
            if issues:
                rejected.append((r, "; ".join(issues)))
                continue
            texts.add((row.get("text") or "").strip())
            fresh.append(row)
        rows.extend(fresh)
        have_ids.update(r["id"] for r in fresh)
        if fresh:
            added.append((fn, len(fresh)))
        line = f"{fn}: принято {len(fresh)}, отклонено {len(rejected)}"
        if rejected:
            n_rejected += len(rejected)
            os.makedirs("batches", exist_ok=True)
            out = os.path.join("batches", "rejected_" + os.path.basename(fn))
            with open(out, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=S.FIELDS, extrasaction="ignore")
                w.writeheader()
                w.writerows([r for r, _ in rejected])
            line += f" → {out}"
            for r, why in rejected:
                print(f"{fn}: строка {r.get('id')} ОТКЛОНЕНА: {why}")
        report.append(line)
        report += [f"  - id {r.get('id')}: {why}" for r, why in rejected]
    if fresh_total := sum(n for _, n in added):
        S.save(rows)
        for fn, n in added:
            print(f"Добавлено {n} строк из {fn}")
        print(f"Теперь в social.csv {len(rows)} строк.")
    os.makedirs("batches", exist_ok=True)
    for fn in files:
        shutil.move(fn, os.path.join("batches", os.path.basename(fn)))
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M UTC} (social)\n")
        for ln in report:
            f.write(("" if ln.startswith(" ") else "- ") + ln + "\n")
    if n_rejected:
        print(f"::warning::Отклонено строк: {n_rejected}. Остальные приняты. Список — batches/_report.md, строки — batches/rejected_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
