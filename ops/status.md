# FOCUS ops status

**Updated:** 2026-10-20 12:15 Kyiv (Grok)

## STATUS: TODO — pad rewrites 24 remain (33→24 this run); ops_report added

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers
- pins.csv total: **326** (incl. 315, 318, 320, 321 fixed)
- Pad phrase remaining: **24** (284, 289–311)
- Metric: use **ops/auto-status.md** (not ready image count). Informational runway ~ to late Nov; promo earlier. Need ~520 more pins by 14.01. Threshold: write batch when info runway < 14 days.

### Actions today
- Restored `social_publish.py` from 56a4622 + PATTERN (owner 19.10) — lint + print_plan back
- `autopilot_prep.py` + heal_social (ready without image → new)
- `pins_batch_3_fix.csv` merged (315, 318, 320, 321)
- Autopilot #24 success (FB Metricool day OK; X 1/1 already scheduled; heal_social cleared ready-without-image)
- ops_report.py added; Check code green
- pins_patch_4: 9/10 accepted (284 rejected — retry next)

### Permanent rules
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)
6. **Backup before edit:** перед правкой важных скриптов (`social_publish.py`, `publish.py`, `merge_*.py`, `autopilot_prep.py`) — сохранить рабочую копию (commit SHA или файл). При поломке сразу восстановить. Не переписывать «по памяти».
7. `social_batch_N.csv`: всегда `status=new`. Product pins: only `ready` with existing image.
8. После merge читать `batches/_report.md`. Отклонённые → `*_fix.csv` в тот же день.
9. Сцены без: laptop, screen, phone, computer, hand(s), person/people, man/woman, girl, boy, human, face.
10. Метрика запаса — `ops/auto-status.md`, не число ready-картинок.
11. **Только улучшение, без порчи:** любые действия с файлами репозитория — максимально аккуратно; допускается только улучшение уже отлаженных процессов. Перед правкой важного скрипта — резерв (commit SHA). Не переписывать «по памяти». Не плодить one-shot workflows. Эффективность > объём правок.

### Claude
- Metricool: дни без Buffer FB
- Typefully / external_posts: без изменений
