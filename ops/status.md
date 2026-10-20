# FOCUS ops status

**Updated:** 2026-10-20 04:37 Kyiv (Grok daily)

## STATUS: TODO — low info stock (32 ready), Autopilot #22 failed on Buffer publish, social_batch_1.csv leftover in root, pad rewrites pending

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers (pins.csv)
- Total: **311**
- new: 181 | ready: 63 (info ready: **32**) | scheduled: 4 | published: 63
- Informational stock days: ~6.4 (STOCK_DAYS=5, target ~90 ready info) — **LOW**

### Actions
- Daily pins latest (#40, 20.10 01:04 UTC): **success**
- Autopilot latest (#22, 20.10 00:36 UTC): **failure** (step «Публикация Facebook и X в Buffer»)

### Leftovers in root
- social_batch_1.csv (S021–S025 + SX021–SX025) — rows already appear in social.csv but file remains
- pins_patch_2.csv, pins_patch_3.csv

### Pending
1. Generate + push next small pins_batch (start id 312, info board, ADHD rules) to refill ready stock
2. Diagnose Autopilot Buffer publish failure; clear or re-trigger social_batch_1
3. Continue description rewrites 264–311 (remove pad phrase) via pins_patch ≤10 rows

### Permanent rules
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)

### Claude
- Metricool: дни без Buffer FB (не каждый 3-й)
- Typefully / external_posts: без изменений
