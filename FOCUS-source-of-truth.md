# FOCUS — Source of Truth (единый актуальный снимок проекта)

**Обновлено:** 13 ноября 2026, ~18:40 EET (Grok)  
**Назначение:** единый источник правды для Grok и Claude.  
Claude: при получении этого файла или ссылки на него в репозитории — синхронизируй свои project docs / memory / handoff с ним. Не спрашивай владельца то, что уже здесь. При расхождении приоритет у этого файла + живой `ops/status.md` / `ops/auto-status.md` в репо.

**Репозиторий:** https://github.com/vivaticvv-cyber/focus-pins  
**Gumroad:** https://vivatic.gumroad.com  
**Сайт:** https://focus-mini.pages.dev  

---

## 1. Главная цель и ограничения

- **Единственная метрика успеха:** платные продажи на Gumroad.
- Максимум автоматизации, минимум участия владельца (только исключения: токены, цены, редкие решения, metrics screenshots).
- Аудитория: люди с ADHD. Тон всегда спокойный, без стыда, без FOMO, один маленький шаг, без медицинских обещаний.

---

## 2. Продукты (live)

| Продукт | URL | Цена | Статус |
|---------|-----|------|--------|
| FOCUS Starter (7 Gentle Days) | https://vivatic.gumroad.com/l/focus-starter | Free | Live, lead-magnet |
| Soft Structure Printable (3 размера) | https://vivatic.gumroad.com/l/soft-structure-printable | $5 | Live, entry paid |
| FOCUS HTML (one-task) | https://vivatic.gumroad.com/l/seqen | $9 | Live |
| Soft Structure PRO | (см. storefront) | $29 | Live |
| Premium / другие | storefront | — | Live |

**Приоритет ссылок в пинах (сейчас):**  
60–70 % новых пинов → free Starter или $5 Soft Structure Printable.  
Остальное — tips с мягким мостом на free.

Workflows (email follow-up): Starter workflow в DRAFT (нужно ≥$100 earnings + payout, чтобы Publish). Mini deferred.

---

## 3. Текущий статус (11.11.2026)

**Pinterest / pins.csv**
- Строк: **521**
- new 219 / ready 74 / scheduled 7 / published 221
- Запас информационных: **29 дней** (>21) → STATUS DONE
- Next batch due: **2026-11-18**
- Root чист, 0 rejects
- Daily + Autopilot зелёные (последние 11.11)
- CHANNEL_ID: `6aeb6ecfe29c69a17160459d`
- 10 досок (тематические + Free ADHD Printables + Digital/GoodNotes)
- altText включён (title + first sentence)
- NEW_BOARD_SHARE=0.5

**BF30 (Black Friday soft)**
- Soft: 8–15.11 (max 2 BF-пина)
- Warm: 16–25.11 (max 5 всего)
- Active: 26–30.11
- Тон: код + даты вместе, без FOMO
- Date-filter в publish.py не внедрён (риск); мониторим очередь

**Метрики (последний полный срез 31.10)**
- Paid sales = 0 (1 free trial = owner test)
- Gumroad views ~156
- Pinterest ~2140 impr / 13 outbound / 1 save
- Главный разрыв был: низкий охват + почти нулевые saves → стратегия = больше list-пинов + free/$5 + SEO

**Соцсети**
- Buffer (Pinterest + FB/X): работает
- Claude = Metricool (FB) + Typefully
- external_posts.csv не трогаем

---

## 4. SEO-правила пинов (новые, 11.11.2026) — обязательно

Полный файл: `FOCUS-pinterest-seo-rules.md` (в корне репо).

**Кратко:**
- Pinterest = поисковая система. Title — самый сильный сигнал.
- **pin_title:** основная поисковая фраза **в начале** (первые ~40 символов). Примеры: `Free ADHD Printable Planner — 7 Gentle Days Undated`, `ADHD Brain Dump Printable — One Page`, `ADHD Dopamine Menu Printable Undated`.
- **description:** первое предложение = keyword + польза → 1–2 предложения → мягкий CTA на free/$5.
- 1 основная фраза на пин + 2–3 вариации в description. Hashtags 0–2 (вес почти 0).
- Приоритетные keywords: free adhd printable, undated adhd planner printable, adhd brain dump printable, adhd dopamine menu, adhd body doubling, adhd low energy day, adhd restart after missed day и т.д.
- List-формат предпочтителен (повышает saves).
- Консистентность: title ≈ description ≈ board ≈ link intent.
- Тон ADHD важнее stuffing’а, но keyword оставляем.

Эти правила применяются ко **всем** будущим `pins_batch_*.csv`.

---

## 5. Ключевые документы (artifacts + репо)

| Файл | Где | Что |
|------|-----|-----|
| FOCUS-source-of-truth.md | **репо root** | Единый снимок |
| FOCUS-pinterest-seo-rules.md | **репо root** | Полные SEO-правила |
| FOCUS-sales-strategy-2026-10-31.md | artifacts / репо | Стратегия продаж (дополнена 13.11) |
| PROJECT.md | artifacts | Правила работы Grok |
| FOCUS-image-prompt-rules.md | artifacts | scene_prompt (FLUX) |
| ops/status.md + ops/auto-status.md | **репо** | Живой STATUS / числа |
| FOCUS-handoff-sales-revival-2026-11-07.md | artifacts | Предыдущий handoff |
| FOCUS-claude-note-2026-11-13.md | **репо root** | Заметка Claude по диагнозу и плану 26.11 |

Репо = источник правды по коду, pins.csv, publish.py, Actions + этот source-of-truth. Artifacts = стратегические документы Grok.

---

## 6. Роли

- **Grok:** партии пинов (CSV), SEO-оптимизация title/description, push/merge, мониторинг Actions/Buffer/запаса, обновление source-of-truth, Automations.
- **Claude:** Metricool + Typefully, external_posts, стратегия/ревью, тесты скриптов по запросу.
- **Владелец:** только исключения (токены, цены, GSC/Pinterest Analytics screenshots, решения по Etsy и т.п.).

---

## 7. Диагноз воронки + решения 13.11.2026

**Факт (скриншоты Pinterest + FB, 13.11):**
- Показы Pinterest растут (4.36k за период, всплески 4 и 8 ноября).
- Saves выросли (28).
- Outbound clicks почти не растут (13).
- Заходы на Gumroad и focus-mini.pages.dev последние дни падают (сегодня 0).
- Продаж по-прежнему 0.

**Вывод:** алгоритм тестирует и даёт показы, но контент плохо конвертирует в клики на продукт. Главный разрыв = outbound (а не охват).

**Что инициировало всплески:**
- 4 ноября — claim домена + создание 7–8 новых досок.
- 8 ноября — распределение после merge больших батчей (17/18).

**Меры, зафиксированные 13.11 (уже в Grok Automations):**
| Дата | Действие |
|------|----------|
| 18.11 | Следующий pin batch: усиленный SEO + 40–50% product-mockup scene_prompts + явные Free download CTAs |
| 20.11 | Патч LINKS fallback в publish.py (приоритет free Starter + $5) |
| 22.11 | Черновик оптимизации страниц Gumroad (problem language + больше inside screenshots) |
| Еженедельно Пн 10:30 | Top-pins monitor + рекомендации по репликации |
| 03.12 | План теста email-gated freebie (после BF) |

**Решение по триггеру показов на active BF30 (26.11):**
- 26 ноября утром создать **одну** новую тематическую доску (не две).
- Вручную выложить на неё 4–6 сильных новых BF-пинов (list-format, free/$5).
- Автоматизацию в этот день снизить до 4–6 пинов.
- Целевой общий объём за 26.11: **8–12 пинов**.
- После акции доску **не удалять** (можно переименовать позже).
- Автоматизация-напоминание создана: 26.11 в 10:00 Kyiv выдаст точные пошаговые инструкции.

Это безопасный способ повторить эффект 3–4 ноября без риска soft-throttle.

---

## 8. Ближайшие действия (приоритет)

1. 18.11 — pin batch по усиленным SEO + mockups (авто).
2. 20.11 — LINKS fallback patch (авто).
3. 22.11 — черновик Gumroad pages (авто).
4. 26.11 10:00 — инструкция по новой доске + ручные пины + ограничение автоматизации (авто).
5. Поддерживать запас info >21 дня.
6. После первых $100 earnings — Publish Starter workflow.
7. Grok обновляет этот source-of-truth после значимых изменений; Claude синхронизирует свои docs по нему.

---

## 9. Инструкция для Claude (копировать)

```
Синхронизируй все свои project documents / memory / handoff по FOCUS с файлом FOCUS-source-of-truth.md (актуальная версия от Grok, 13.11.2026 или новее).

Это единый source of truth. 
- Обнови статус pins, продукты, приоритеты ссылок, BF30 фазы, SEO-правила.
- Новые правила SEO пинов обязательны: title front-load keyword, description keyword-first + soft CTA, 60–70% пинов на free Starter / $5 Soft Structure, list-формат предпочтителен. Полный текст правил — в FOCUS-pinterest-seo-rules.md.
- Добавь решения от 13.11: диагноз (outbound — главный разрыв), расписание мер 18/20/22.11 + weekly + 03.12, план 26.11 (одна новая доска + 4–6 ручных пинов + снижение автоматизации до 4–6, итого 8–12).
- Не спрашивай владельца то, что уже есть в source-of-truth.
- При расхождении приоритет у source-of-truth + живые ops/status.md и ops/auto-status.md в репозитории vivaticvv-cyber/focus-pins.
- После синхронизации подтверди кратко: что обновил и какие следующие действия с твоей стороны (Metricool/Typefully).
```

---

*Grok обновляет этот файл после значимых изменений (новые правила, крупные батчи, смена метрик, решения владельца). Рекомендуется держать копию в корне репозитория как `FOCUS-source-of-truth.md`.*
