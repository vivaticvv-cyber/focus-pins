# FOCUS ops status

**Updated:** 2026-10-21 ~22:30 Kyiv (Grok, help-6 applied)

## STATUS: DONE

### help-6 results
- ops-report.yml: добавлен `workflow_run` после Autopilot / Daily pins / Merge pins batch → auto-status всегда свежий
- Правила статуса обновлены (раздел ниже): нет «Idle», всегда Next batch due, DONE только при квоте + 0 reject
- Недельный график производства (из help-6 §1.1) внесён; порог тревоги запаса = 21 день
- Банк идей (73 info + 27 promo) сохранён в FOCUS-grok-help-6.md (артефакт / контекст)

### Current numbers (из auto-status 21.10 09:33 UTC)
- pins.csv: **360** (new 220, ready 66, scheduled 6, published 68)
- Info runway: 228 (~до 26.11), **36 дн.** → норма
- Promo runway: 58 (~до 23.11)
- Social: S ready 21, SX ready 20, M ready 20; 0 без картинки
- Pad=0, shifted=0, reject=0

### GitHub Actions
- Merge #19 success, Autopilot #27 success, Daily #43 success, Check code green

### Next batch due: 2026-10-28
Квота к ближайшему вторнику (04.11): **+0 info / +6 promo** (из графика help-6).  
Далее еженедельно ≈52 info + 15 promo (половина promo — product pins через product_specs_N.csv).

### STATUS rules (help-6 §4)
1. STATUS: DONE = последний цикл без отклонений **и** выполнена недельная квота; иначе IN PROGRESS с остатком.
2. В каждом статусе: `Next batch due: <дата>` + числа запаса из auto-status.
3. Слово «Idle» не используется. После DONE всегда указана дата следующей сессии.

### NEED OWNER
- Создать Automation в Grok (Tasks) с текстом из help-6 §1.2 (каждые 2 дня, утро Киев). Без этого производство остановится при отсутствии чата.
- Решение по MAX_PER_DAY (сейчас 10).
- metrics.md: 25.10 и 31.10.
