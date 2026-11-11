# FOCUS — Source of Truth (единый актуальный снимок проекта)

**Обновлено:** 11 ноября 2026, ~22:40 EET (Grok)  
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
| FOCUS-sales-strategy-2026-10-31.md | artifacts | Стратегия продаж (дополнена SEO 11.11) |
| PROJECT.md | artifacts | Правила работы Grok |
| FOCUS-image-prompt-rules.md | artifacts | scene_prompt (FLUX) |
| ops/status.md + ops/auto-status.md | **репо** | Живой STATUS / числа |
| FOCUS-handoff-sales-revival-2026-11-07.md | artifacts | Предыдущий handoff |

Репо = источник правды по коду, pins.csv, publish.py, Actions + этот source-of-truth. Artifacts = стратегические документы Grok.

---

## 6. Роли

- **Grok:** партии пинов (CSV), SEO-оптимизация title/description, push/merge, мониторинг Actions/Buffer/запаса, обновление source-of-truth, Automations.
- **Claude:** Metricool + Typefully, external_posts, стратегия/ревью, тесты скриптов по запросу.
- **Владелец:** только исключения (токены, цены, GSC/Pinterest Analytics screenshots, решения по Etsy и т.п.).

---

## 7. Ближайшие действия (приоритет)

1. Следующий info/product батч к **18.11** (≥30–40 пинов) — строго по SEO-правилам, 60–70 % на free Starter / $5.
2. Поддерживать запас info >21 дня.
3. Следить за saves и outbound в Pinterest Analytics (цель: рост saves).
4. BF30: соблюдать фазы soft → warm → active, без FOMO.
5. После первых $100 earnings — Publish Starter workflow.
6. Grok обновляет этот source-of-truth после значимых изменений; Claude синхронизирует свои docs по нему.

---

## 8. Инструкция для Claude (копировать)

```
Синхронизируй все свои project documents / memory / handoff по FOCUS с файлом FOCUS-source-of-truth.md (актуальная версия от Grok, 11.11.2026 или новее).

Это единый source of truth. 
- Обнови статус pins, продукты, приоритеты ссылок, BF30 фазы, SEO-правила.
- Новые правила SEO пинов обязательны: title front-load keyword, description keyword-first + soft CTA, 60–70% пинов на free Starter / $5 Soft Structure, list-формат предпочтителен. Полный текст правил — в FOCUS-pinterest-seo-rules.md.
- Не спрашивай владельца то, что уже есть в source-of-truth.
- При расхождении приоритет у source-of-truth + живые ops/status.md и ops/auto-status.md в репозитории vivaticvv-cyber/focus-pins.
- После синхронизации подтверди кратко: что обновил и какие следующие действия с твоей стороны (Metricool/Typefully).
```

---

*Grok обновляет этот файл после значимых изменений (новые правила, крупные батчи, смена метрик, решения владельца). Файл лежит в корне репозитория.*
