# FOCUS ops status

**Updated:** 2026-11-26 ~11:20 Kyiv (Grok — Buffer cleaned + MAX_PER_DAY=6)

## STATUS: DONE

pins=614. Info stock ~22d (>21). Root clean expected after upload. Next batch due 2026-12-02.

### Numbers
- pins.csv: published ~362, new 177, ready 72, scheduled 3 (сегодня: 385, 447, 455)
- **MAX_PER_DAY = 6** (с 27.11.2026)

### Сегодня 26.11 (сделано Grok)
- Buffer: удалены 4 лишних scheduled (320, 321, 425, 434) → status=ready в pins.csv
- 358 уже ушёл (published)
- Осталось авто сегодня: 3 (≤4)
- Ручные 4–6 на новую доску — по инструкции утра

### Решение
- 26.11: авто ≤4
- С 27.11: MAX_PER_DAY=6 постоянно

### NEED
- Загрузить в репо: publish.py (полный с MAX_PER_DAY=6), pins.csv, FOCUS-source-of-truth.md
