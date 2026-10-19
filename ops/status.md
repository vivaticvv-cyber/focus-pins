# FOCUS ops status

**Updated:** 2026-10-19 ~22:20 Kyiv (Grok)

## STATUS: TODO (description rewrite in progress)

### Success criterion
- Метрика: продажи Gumroad. Сейчас **0**. Контроль: **31.10.2026**.

### Claude fixes 19.10 — сделано
1. ✅ Удалён `.github/workflows/restore-publish.yml`
2. ✅ `merge_batch.py` — построчный accept/reject, **без** auto-pad / `_PAD`
3. ✅ `merge_social.py` — построчный accept/reject
4. ✅ `social_publish.py` PATTERN Facebook = `(3, (0,))` (каждый 3-й день); X = каждый день кроме Typefully
5. ✅ Удалён корневой `pins_patch_1.csv`
6. ⏳ **Осталось:** переписать 47 описаний ids 264–311 (кроме 267) — убрать фразу «A small visible step…», длина 340–420, хэштеги в конце. Частями ≤10 через `pins_patch_2+`.

### Done earlier 19.10
- pins.csv = 311; Daily #39 stock full (info ready 29/29)
- social_batch_1 в корне (S021–S025 + SX021–SX025) — ждёт Autopilot merge

### Next (Grok)
1. pins_patch: 264–290 first, then 291–311 (≤10 per file)
2. After patches: lint clean, no pad phrase
3. Monitor Autopilot for social_batch_1

### Permanent rules (updated)
1. Скрипты не меняют авторский текст (никакой автодобивки)
2. Плохая строка отклоняется отдельно; остальные принимаются
3. Нет workflows, перезаписывающих исходники из истории
4. PATTERN / STOCK_DAYS только с записью в ops/log.md
5. Facebook Buffer = каждый 3-й день (решение владельца 19.10)

### Claude
- Metricool: дни без Buffer FB (не каждый 3-й)
- Typefully / external_posts: без изменений
