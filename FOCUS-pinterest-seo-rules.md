# FOCUS — правила SEO-оптимизации пинов Pinterest

**Дата:** 11.11.2026  
**Цель:** максимизировать показы (impressions), сохранения (saves) и outbound-клики на free Starter и $5 Soft Structure Printable.  
**Источник:** анализ pins.csv + актуальные best practices Pinterest SEO 2026 + sales strategy.

Pinterest — поисковая система. Ранжирование: relevance (keywords) + engagement (saves + outbound clicks) + uniqueness + consistency title/image/board/landing page.

Эти правила обязательны при подготовке любого нового `pins_batch_*.csv`.

---

## 1. Иерархия сигналов (где ставить ключевые фразы)

| Приоритет | Место | Что делать |
|-----------|--------|------------|
| 1 (высший) | **pin_title** | Основная поисковая фраза в **начале** title |
| 2 | **description** (первое предложение) | Та же или близкая фраза + польза |
| 3 | **board** | Keyword-название доски (уже есть) |
| 4 | **alt text** | Уже автоматически = title + первое предложение |
| 5 | Текст на картинке (если есть) | Краткий headline, совпадающий с title |
| — | Hashtags | 0–2 максимум. Вес почти нулевой. Не рассчитывать на них. |

Один пин = **одна основная поисковая фраза**. 2–3 вариации — только в description.

---

## 2. Формула pin_title (макс. 100 символов, идеал 40–80)

**Структура:**  
`[Основная поисковая фраза] — [выгода / уточнение]`

**Правила:**
- Основная фраза **в первых 40 символах** (мобильный превью).
- Начинать с «ADHD …» или «Free ADHD …» / «Undated ADHD …» — это наш front-load.
- Быть описательным, а не «умным» или загадочным. Pinterest ищет буквально.
- Для product-пинов (free / $5) обязательно включать: `printable`, `free`, `undated`, `planner` или конкретную страницу (`brain dump`, `dopamine menu`, `daily focus`).

**Хорошо:**
- `Free ADHD Printable Planner — 7 Gentle Days Undated`
- `ADHD Brain Dump Printable — One Page, No Overwhelm`
- `ADHD Dopamine Menu Printable Undated`
- `ADHD Stuck Start: 5 Things You Can Do in Five Minutes`
- `Undated ADHD Planner Printable — Letter, A4 & A5`

**Плохо:**
- `A Kinder Way to Start Your Day` (нет keyword)
- `My Favorite ADHD Hack` (vague)
- `Try This Soft Reset` (не поисковая фраза)

---

## 3. Формула description (300–450 символов, лимит 500)

**Структура (3 части):**
1. Первое предложение = основная keyword-фраза + кто/что.
2. 1–2 предложения пользы / что внутри / как использовать (спокойный ADHD-тон).
3. Мягкий CTA + что получит после клика (free download / $5 printable).

**Правила:**
- Keyword в **первом предложении**.
- 2–3 естественные вариации дальше (не stuffing).
- Тон: тёплый, без стыда, один маленький шаг, без FOMO.
- В конце — явный мотив кликнуть: «скачай free Starter», «48 undated pages for $5», «print today».
- Hashtags: максимум 2–3 в самом конце или убрать.

**Пример (free Starter):**
```
Free ADHD printable planner pages help many brains start without a long setup. The Starter pack gives you Daily Focus, Brain Dump and a gentle restart page — undated, print at home, no signup. Use one page on a hard day and leave the rest. Download the free FOCUS Starter and try one soft page today.
```

**Пример ($5 Soft Structure):**
```
ADHD dopamine menu printable keeps tiny rewards visible when motivation is low. Soft Structure includes a ready Dopamine Menu page plus Daily Focus and Brain Dump — 48 undated pages in Letter, A4 and A5 for $5. Print the pages you need and add more later. Get the Soft Structure printable and keep one page on your desk.
```

---

## 4. Product vs Tip пины — разные приоритеты

| Тип | Цель | Title акцент | Link | Board предпочтение |
|-----|------|--------------|------|--------------------|
| **Product (free / $5)** | Клики + saves | Free / Printable / Undated / конкретная страница | focus-starter или soft-structure-printable | Free ADHD Printables (Undated) или тематическая |
| **Tip / List** | Saves + trust → потом клик | ADHD [проблема]: [список / решение] | free Starter (предпочтительно) | ADHD Tips & Focus Hacks или точная тематическая |

- List-формат (1) 2) 3) …) сильно повышает saves — использовать везде, где естественно.
- Не меньше 60–70 % новых пинов в ближайшие недели должны вести на free Starter или $5.

---

## 5. Приоритетный keyword-банк (обновлять по Analytics)

Использовать эти фразы в первую очередь (проверены по нише + спросу):

**Высокий приоритет (product):**
- free adhd printable / free adhd planner printable
- undated adhd planner printable
- adhd brain dump printable
- adhd dopamine menu printable
- adhd daily focus printable
- adhd planner for adults undated
- printable adhd planner letter / a4

**Средний (tips + product bridge):**
- adhd body doubling
- adhd low energy day
- adhd decision fatigue
- adhd restart after missed day / shame spiral
- adhd morning routine / evening routine
- adhd overwhelm reset
- adhd half finished tasks

**Сезонные / контекст:**
- adhd holidays / new year reset (мягко)
- adhd work from home / study focus

При подготовке батча: выбрать 1 основную фразу на пин из этого банка.

---

## 6. Консистентность (обязательная проверка перед merge)

Перед тем как считать пин готовым, проверить:

1. **pin_title** содержит основную keyword-фразу в начале.
2. **description** начинается с той же или очень близкой фразы.
3. **board** соответствует теме (Free Printables для product, Tips/Work/Overwhelm для советов).
4. **link** ведёт на правильный продукт (free → focus-starter, $5 → soft-structure-printable).
5. Image text (если будет) не противоречит title.
6. Тон спокойный, без давления, один маленький шаг.

Если title про «free printable», а link на focus-mini.pages.dev без продукта — исправить.

---

## 7. Чего избегать

- Keyword stuffing (одна фраза 4+ раза).
- «Умные» или поэтические title без поисковых слов.
- Длинные title > 85–90 символов.
- Hashtag-спам.
- Разный intent в title и link.
- Обещания, которых нет на landing page.
- FOMO, «last chance», жёсткие дедлайны (нарушает ADHD-тон и BF-стратегию).

---

## 8. Как применять при создании батча

1. Определить тип пина (product free / product $5 / tip-list).
2. Выбрать **одну** основную фразу из keyword-банка.
3. Написать pin_title по формуле §2.
4. Написать description по формуле §3.
5. Выбрать board и link.
6. Прогнать чек-лист §6.
7. Предпочитать list-формат для saves.

Эти правила дополняют существующие (calm tone, scene_prompt rules, board_map, publish.py). При конфликте с тоном ADHD — тон важнее, но keyword оставляем.

**Файл в репо:** `FOCUS-pinterest-seo-rules.md`

---

*Обновлять keyword-банк после каждого крупного Analytics-среза (раз в 2–4 недели) на основе реальных impressions/saves.*
