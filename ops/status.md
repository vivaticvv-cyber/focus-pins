# FOCUS ops status

**Updated:** 2026-11-26 ~10:45 Kyiv (Grok — limit change)

## STATUS: DONE (с правкой лимита)

pins=614. Info stock 22d (>21). Root clean. Actions green. 0 rejects. Next batch due 2026-12-02.

### Numbers
- pins.csv: 614 rows (new 177, published 361, ready 68, scheduled 8 → цель сегодня: оставить 4 авто)
- Info unpublished (new+ready): ~153–159, stock ~21–22d
- Promo unpublished: ~92–94
- Next batch due: **2026-12-02**
- **MAX_PER_DAY = 6** (с 27.11.2026; было 10). Сегодня 26.11 вручную: авто ≤4

### BF30
- Active phase 26.11–30.11
- Сегодня: новая доска + 4–6 ручных + авто ≤4 (итого 8–12)
- Tone: code + dates together, no FOMO

### Решение 26.11 (владелец)
- 26.11: авто-пины Pinterest ≤4 (оставить самые важные free Starter / $5 / BF; лишние снять из Buffer)
- С 27.11: постоянный лимит **6 пинов/сутки** (MAX_PER_DAY=6 в publish.py) — цель рост показов при безопасном объёме

### Claude (Metricool/Typefully)
- Ongoing as planned

### NEED OWNER (сегодня)
1. Buffer → очередь Pinterest на 26.11: оставить **4** пина, остальные удалить из очереди.
   Предпочтительно оставить: 358 (BF30), 385 (free Starter), 447 ($5), 455 ($5).
   Снять: 320, 321, 425, 434 (tips / pages.dev / dwshkr).
2. После снятия в Buffer: в pins.csv у снятых поставить status=ready, очистить scheduled_at и buffer_post_id (или оставить — следующий Daily не тронет published/scheduled; при status=scheduled без поста в Buffer будет рассинхрон — лучше ready).
3. Ручные 4–6 на новую доску — по инструкции утра.

### NEED
- Выполнить пункты выше сегодня.
