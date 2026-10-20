# FOCUS ops status

**Updated:** 2026-10-20 06:46 Kyiv (Grok insurance)

## STATUS: TODO — pins.csv ~319 (317-321 partial merge), next info batch 322-326 pushed + merge triggered, stock still low, rewrites pending

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Current numbers (pins.csv)
- Total: **~319** (317-321 partial; 322-326 pending merge)
- new: ~186 | ready: 63 (info ready: ~37) | scheduled: 4 | published: 63
- Informational stock days: ~7.4 (STOCK_DAYS=5, target ~90 ready info) — **LOW**

### Actions
- Daily pins latest (#40): **success**
- Autopilot latest (#22): **failure** (SyntaxError fixed in social_publish.py)
- Merge #7 (317-321): **success** (partial accept)
- Merge triggered for pins_batch_3.csv (322-326)

### Leftovers in root
- pins_batch_3.csv (322-326) — merge triggered
- (no other batch/patch files in root)

### Pending
1. Confirm merge of 322-326; generate next small info batch if still low
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
