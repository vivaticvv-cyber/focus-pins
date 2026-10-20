# FOCUS ops status

**Updated:** 2026-10-20 04:50 Kyiv (Grok insurance)

## STATUS: TODO — merge of pins_batch_1 (312-316) triggered, stock still low after, Autopilot syntax fixed, leftovers cleared

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers (pins.csv)
- Total: **311** (batch 312-316 pending merge)
- new: 181 | ready: 63 (info ready: **32**) | scheduled: 4 | published: 63
- Informational stock days: ~6.4 (STOCK_DAYS=5, target ~90 ready info) — **LOW**

### Actions
- Daily pins latest (#40): **success**
- Autopilot latest (#22): **failure** (SyntaxError in social_publish.py — fixed)
- Merge pins batch triggered for pins_batch_1.csv

### Leftovers in root
- pins_batch_1.csv (312-316) — merge triggered
- (social_batch_1, pins_patch_2/3 deleted)

### Pending
1. Confirm merge of 312-316; generate next small info batch if still low
2. Continue description rewrites 264–311 (remove pad phrase) via pins_patch ≤10 rows
3. Re-run Autopilot after syntax fix if needed for Buffer publish

### Permanent rules
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)

### Claude
- Metricool: дни без Buffer FB (не каждый 3-й)
- Typefully / external_posts: без изменений
