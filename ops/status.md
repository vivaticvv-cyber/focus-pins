# FOCUS ops status

**Updated:** 2026-10-20 12:00 Kyiv (Grok — Claude help-2 applied)

## STATUS: TODO — social_publish restored; heal_social; 4 pins fixed; 33 pad rewrites remain

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers
- pins.csv total: **326** (incl. 315, 318, 320, 321 fixed)
- Pad phrase remaining: **33** (274, 275, 277, 282–311)
- Metric: use **ops/auto-status.md** (not ready image count). Informational runway ~ to late Nov; promo earlier. Need ~520 more pins by 14.01. Threshold: write batch when info runway < 14 days.

### Actions today
- Restored `social_publish.py` from 56a4622 + PATTERN (owner 19.10) — lint + print_plan back
- `autopilot_prep.py` + heal_social (ready without image → new)
- `pins_batch_3_fix.csv` merged (315, 318, 320, 321)
- One-shot restore-social-publish.yml to be removed after success
- Next: Autopilot run (X 20.10), ops_report + check-code workflows

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

### Claude
- Metricool: дни без Buffer FB
- Typefully / external_posts: без изменений
