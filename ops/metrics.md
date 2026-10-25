# FOCUS metrics

Контрольные точки: **25.10** и **31.10.2026**. Критерий успеха проекта = продажи Gumroad.

| дата | Gumroad: просмотры страниц (soft-structure / seqen / premium-pack / dwshkr) | Gumroad: источники трафика | скачивания Mini | focus-mini.pages.dev: посетители (Cloudflare) | Pinterest: показы / клики по ссылкам / подписчики | Facebook: охват / клики | X: показы / клики | продажи (шт., $) |
|------|--------------------------------------------------------------------------|----------------------------|-----------------|-----------------------------------------------|---------------------------------------------------|-------------------------|-------------------|------------------|
| 25.10 | **Все товары (16.09–25.10): 142 views.** Per-product не снимали. sales_count: 0/0/0/1 | Direct/email/IM 117; vivatic.gumroad.com 17; FB 5; focus-mini 1; Google 1; Reddit 1 | 1 (29.09, free; **тест владельца**) | **RUM ≈ Exclude bots:** ~50 visits / ~50 page views за ~30д. Last 7d: 7. Edge (боты): ~2740 visits | — | — | — | **paid 0** ($0). free trial 1 = self-test |
| 31.10 | | | | | | | | |

## Снимок 25.10.2026 (API + dashboard screenshots владельца)

### Cloudflare (trial focus-mini.pages.dev)
- **KPI (живые):** RUM ≈ Web Analytics Exclude bots → **~50 visits / ~50 page views** (25.09–25.10).
- Last 7 days: **7** visits.
- Edge (с ботами, не KPI): ~8920 requests, ~2740 visits.

### Gumroad Dashboard (16.09–25.10, All products)
Источник: скриншоты Analytics → Продажи.

| Метрика | Значение |
|---------|----------|
| Views (Мнения) | **142** |
| Sales (Продажи) | 1 |
| Revenue | **$0** |
| Conversion | ~0,7% (1/142; единственная продажа = self-test) |

**Referrers (views / sales):**
| Источник | Views | Sales |
|----------|-------|-------|
| Прямая связь / email / IM | 117 | 1 |
| vivatic.gumroad.com | 17 | 0 |
| Facebook | 5 | 0 |
| focus-mini.pages.dev | 1 | 0 |
| Google | 1 | 0 |
| Reddit | 1 | 0 |

**Locations:** US 93 views / 0 sales; UA 6 views / 1 sale (тест).

**По продуктам (API sales_count):** soft-structure 0, seqen 0, premium-pack 0, dwshkr 1 (self-test). Per-product views в dashboard не снимали — при желании можно добавить позже.

### Соцсети
Не снимались отдельно. Из referrers: FB дал 5 views на Gumroad; Pinterest в списке referrers не виден (возможно уходит в Direct).

## Краткий вывод по воронке (25.10, обновлён)
1. **На Gumroad есть views (142 за ~40 дней)** — люди доходят до страниц товаров. Это сильнее, чем только CF trial (~50).
2. **Paid = 0.** Единственная «продажа» Mini — self-test владельца.
3. **Главный поток views = Direct / email / IM (117).** Соцсети пока почти не конвертируют в Gumroad-views: FB 5, Reddit 1, Pinterest не виден в referrers.
4. Trial → Gumroad почти не течёт (focus-mini.pages.dev = 1 referrer).
5. US даёт больше всего views (93), но 0 продаж; конверсии реальных ещё нет.
6. Узкое место: **слабый переход из соцсетей/пинов на страницы товаров + отсутствие реальных покупок.** До 31.10 — без паники, продолжаем автоматизацию. На 31.10 смотрим, выросли ли views из FB/Pinterest и появились ли paid.

## Правило решения на 01.11
- нет трафика на страницы товаров → проблема в источниках трафика
- трафик есть, на товар не идут → ссылки / посадка
- на страницы приходят, но не покупают → страница, цена, доверие (отзывов и продаж пока нет)

Пороги «достаточно трафика» определяются по данным 31.10, заранее не придумываем.
