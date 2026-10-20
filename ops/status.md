# FOCUS ops status

**Updated:** 2026-10-20 05:46 Kyiv (Grok insurance)

## STATUS: TODO — pins.csv=316 (312-316 merged), next info batch 317-321 pushed + merge triggered, stock still low, rewrites pending

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers (pins.csv)
- Total: **316** (312-316 merged; 317-321 pending merge)
- new: ~186 | ready: 63 (info ready: ~37) | scheduled: 4 | published: 63
- Informational stock days: ~7.4 (STOCK_DAYS=5, target ~90 ready info) — **LOW**

### Actions
- Daily pins latest (#40): **success**
- Autopilot latest (#22): **failure** (SyntaxError fixed in social_publish.py)
- Merge #6 (312-316): **success**
- Merge triggered for pins_batch_2.csv (317-321)

### Leftovers in root
- pins_batch_2.csv (317-321) — merge triggered
- (no other batch/patch files in root)

### Pending
1. Confirm merge of 317-321; generate next small info batch if still low
2. Continue description rewrites 264–311 (remove pad phrase) via pins_patch ≤10 rows
3. Re-run Autopilot after syntax fix if Buffer day needs publish

### Permanent rules
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)

### Claude
- Metricool: дни без Buffer FB (не каждый 3-й)
- Typefully / external_posts: без изменений
