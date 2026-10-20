# FOCUS ops status

**Updated:** 2026-10-20 12:30 Kyiv (Grok — Claude help-3)

## STATUS: TODO — pad 23 remain (289–311); 5 promo still have shifted link columns

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**. Таблица: `ops/metrics.md` (владелец заполняет 25.10 и 31.10).

### Current numbers
- pins.csv total: **326**
- Pad phrase remaining: **23** (289–311)
- Shifted columns (new + scheduled_at filled): **5** (289, 294, 299, 304, 309) — fix when rewriting those descriptions (put URL in `link`)
- Metric: `ops/auto-status.md`. Threshold: write batch when info runway < 14 days.

### Actions today (help-3)
- `pins_patch_5`: 267+284 links fixed (link filled, scheduled_at empty)
- `merge_batch.py` + `merge_social.py`: shape_issue / extra columns rejection
- `ops_report.py`: reports shifted columns
- Removed `restore-social-publish.yml`, leftover `pins_patch_4.csv`
- `ops/metrics.md` created
- Check code green; merge_batch syntax verified

### Permanent rules
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)
6. **Backup before edit:** перед правкой важных скриптов — commit SHA. При поломке сразу восстановить. Не переписывать «по памяти».
7. `social_batch_N.csv`: всегда `status=new`. Product pins: only `ready` with existing image.
8. После merge читать `batches/_report.md`. Отклонённые → `*_fix.csv` в тот же день.
9. Сцены без: laptop, screen, phone, computer, hand(s), person/people, man/woman, girl, boy, human, face.
10. Метрика запаса — `ops/auto-status.md`, не число ready-картинок.
11. **Только улучшение, без порчи.** Не плодить one-shot workflows. Эффективность > объём правок.
12. **CSV quoting:** все текстовые поля партий/патчей в двойных кавычках; 13 колонок; перед push — предпроверка (длина 340–420, хэштеги в конце, link только в колонке link, scheduled_at пуст у new).

### Claude
- Metricool: дни без Buffer FB
- Typefully / external_posts: без изменений
