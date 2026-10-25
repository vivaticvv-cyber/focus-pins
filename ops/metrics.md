# FOCUS metrics

Контрольные точки: **25.10** и **31.10.2026**. Критерий успеха проекта = продажи Gumroad.

| дата | Gumroad: просмотры страниц (soft-structure / seqen / premium-pack / dwshkr) | Gumroad: источники трафика | скачивания Mini | focus-mini.pages.dev: посетители (Cloudflare) | Pinterest: показы / клики по ссылкам / подписчики | Facebook: охват / клики | X: показы / клики | продажи (шт., $) |
|------|--------------------------------------------------------------------------|----------------------------|-----------------|-----------------------------------------------|---------------------------------------------------|-------------------------|-------------------|------------------|
| 25.10 | **нет в API** (только dashboard). sales_count: 0 / 0 / 0 / 1 | — | 1 (29.09, free; **тест владельца**) | **RUM ≈ Exclude bots:** ~50 visits / ~50 page views за ~30д (25.09–25.10). Last 7d: 7. 23.10=5, 24.10=1. Edge (с ботами): ~2740 visits / 8920 req | — | — | — | **paid 0** ($0). free trial 1 = self-test |
| 31.10 | | | | | | | | |

## Снимок 25.10.2026 (утро + правка, Grok API)

### Cloudflare (trial focus-mini.pages.dev)
- **KPI (живые):** RUM `rumPageloadEventsAdaptiveGroups` ≈ Web Analytics Exclude bots → **~50 visits / ~50 page views** за период 25.09–25.10.
- Last 7 days: **7** visits.
- Edge HTTP (включая ботов, не KPI): ~8920 requests, ~2740 visits.
- Источник: Cloudflare GraphQL Account Analytics (token Read analytics).

### Gumroad (API view_sales + edit_products + products)
| Товар | Permalink | sales_count | paid |
|-------|-----------|-------------|------|
| Soft Structure Premium | soft-structure | 0 | 0 |
| One Task ADHD Planner | seqen | 0 | 0 |
| Premium Complete Pack | premium-pack | 0 | 0 |
| FOCUS Mini 7-Day Free Trial | dwshkr | 1 | 0 (free, 2026-09-29) |

- **Paid sales total: 0.** Revenue: $0.
- **Единственная «продажа» Mini (29.09) — тест владельца** (проверка, как работает checkout). В воронке как органическую не считаем.
- **Page views / referrers:** публичный Gumroad API **не отдаёт**. Проверено: `view_sales` + `edit_products` → products/sales дают только `sales_count` / `sales_usd_cents` и список продаж. Endpoints `/analytics`, `/stats`, `/views`, product subpaths — 404 или «not found». Официальная документация подтверждает: views есть только в Sales Analytics dashboard (UI). Для 25.10 views = N/A через API.

### Соцсети / Pinterest / FB / X
Не снимались в этой точке (не критично для 25.10; при 31.10 — по dashboard при желании).

## Краткий вывод по воронке (25.10)
1. **Живой трафик на trial очень низкий** (~1–2 визита/день в среднем, всплеск 23.10). Edge-тысячи — боты.
2. **Продаж paid = 0.** Единственный free trial 29.09 — self-test владельца, не реальный клиент.
3. Воронка на этапе **обнаружения / трафика**, а не конверсии: данных по «пришли на товар → не купили» почти нет.
4. GSC ещё не проиндексировал — ожидаемо, не блокирует текущую автоматизацию соцсетей.
5. До **31.10** продолжаем автоматизацию (pins/social) без изменений оффера/цен. Если 31.10 всё ещё 0 paid — разбор: ссылки в постах, посадка trial→Gumroad, видимость в Pinterest.

## Правило решения на 01.11
- нет трафика на страницы товаров → проблема в источниках трафика
- трафик есть, на товар не идут → ссылки / посадка
- на страницы приходят, но не покупают → страница, цена, доверие (отзывов и продаж пока нет)

Пороги «достаточно трафика» определяются по данным 31.10, заранее не придумываем.
