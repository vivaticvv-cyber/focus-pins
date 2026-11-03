# FOCUS — handoff-8 (3 ноября 2026)

Заменяет handoff-7. Читать вместе с:
- FOCUS-marketing-brief-8.md (Claude)
- FOCUS-blackfriday-bf30-plan.md
- FOCUS-grok-tasks-2026-11-03.md
- FOCUS-sales-strategy-2026-10-31.md (v2)
- PROJECT.md

**Главная цель:** продажи на vivatic.gumroad.com. Максимум автоматизации, минимум участия владельца.

---

## Сделано 3 ноября (этот чат)

1. **Pinterest domain claimed** — `focus-mini.pages.dev` успешно подтверждён. Meta `p:domain_verify` live.
2. **7 новых досок** созданы владельцем (названия ниже). Buffer пока видит только старые 2 (лаг) — при следующем get_channel / публикации подхватит.
3. **Сайт** (архив `focus-mini-site-funnel-2026-11-03-pinterest-claim.zip`):
   - meta Pinterest + Google сохранены
   - баннер BF: «All paid FOCUS tools», автоскрытие после 1.12 10:00 Киев
   - таблица сравнения: HTML больше не «fillable»
   - описание $5 приведено к реальному составу
   - «Enter 0» убрано со Starter
4. Gumroad-правки 2.11 (кросс-ссылки, receipts, браузеры, убран Enter 0 с Mini) остаются в силе. Profile = Vivatic Studio.

## Доски (созданы владельцем 3.11)

| # | Название | Тип |
|---|----------|-----|
| 1 | ADHD Morning & Evening Routines | info |
| 2 | ADHD Overwhelm & Reset Tools | info |
| 3 | ADHD Work & Study Focus | info |
| 4 | ADHD Home & Low-Energy Chores | info |
| 5 | ADHD Holidays, Gifts & Budget | info |
| 6 | Free ADHD Printables (Undated) | promo |
| 7 | ADHD Digital Planner & GoodNotes | promo |

Старые 2 не трогаем: ADHD Tips & Focus Hacks (info), FOCUS – ADHD Planner (promo).

## Что дальше (приоритет)

### Сразу (Grok)
1. Получить serviceId новых досок (Buffer get_channel, когда подтянет, или вручную из URL досок).
2. Вписать в CONFIG `publish.py` + **обязательно** `board_kind` (info/promo). Иначе риск аварии 16.10.
3. Окно дат для пинов 367–374 (BF): публиковать только 16.11–1.12. Распределить 3–4 на 16–25.11, остальные на 26.11–1.12.
4. Загрузить свежий `external_posts.csv` в репозиторий.
5. Следующая партия пинов (~50 строк) до 15.11 — с новыми досками, ~40% list-format, сезонные темы.

### До 7 ноября
- Таблица Etsy (10–15 листингов) — если ещё не сделана.
- Проверка BF30 «Applies to» (уже была ок 2.11, можно перепроверить).

### 16–25 ноября
- Прогрев BF30: строка в профилях, пины/посты с кодом + датами.

### 26.11 – 1.12
- Каждый день FB/X + пины, строки на 4 платных страницах Gumroad.

### 2 декабря
- Убрать всё про BF30.

## Владельцу больше ничего срочного
- Domain claim и доски — сделано.
- Печать Starter и скриншоты Analytics — по возможности, не блокирует.

## Facebook / Twitter domain claim
**Не нужно** сейчас. У Pinterest claim даёт алгоритмический плюс. У FB/X аналогичной механики для нашего случая нет.

## Состояние на 3.11
- pins.csv ≈ 374, info stock хватает примерно до 20–26.11 → партия нужна до 15.11.
- Paid sales = 0. Starter workflow = draft (ждёт $100).
- Metricool/Typefully ведёт Claude по своим файлам.
- Автоматизации Grok: daily ops 4:30, batch continue 4:45–7:00 Киев — работают.

## Устаревшее (не делать)
- Добавлять «Enter 0» на бесплатные товары.
- Менять название профиля (уже Vivatic Studio).
- Пытаться Publish Workflow Starter до $100 earnings.
- Трогать уже сделанные 2.11 правки Gumroad.
