# FOCUS — Source of Truth (единый актуальный снимок проекта)

**Обновлено:** 18 ноября 2026, ~16:15 EET (Grok)  
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

## 3. Текущий статус (18.11.2026, после fix batch_20)

**Pinterest / pins.csv**
- Строк: **560** (после pins_batch_20_fix: +32, ids 532–567 без 4 дублей)
- Статусы (на момент Claude/ops ~12:21 UTC): published 288, new 195, ready 70, scheduled 7
- Info неопубликованных: 183 → хватит до ~13.12 (≈25 дн., норма); до 14.01 докупить ≈237
- Промо: 82 → хватит до ~28.12; до 14.01 докупить ≈37
- Next batch due: **2026-11-25**
- Root чист, 0 ложных rejects (intentional title-dupe rejects удалены 18.11)
- Daily + Autopilot зелёные
- CHANNEL_ID: `6aeb6ecfe29c69a17160459d`
- 10 досок, altText включён, NEW_BOARD_SHARE=0.5

**BF30 (Black Friday soft)**
- Soft: 8–15.11 (max 2) — завершён
- Warm: 16–25.11 (max 5 всего) — сейчас
- Active: 26–30.11
- Тон: код + даты вместе, без FOMO
- Date-filter в publish.py не внедрён (риск); мониторим очередь

**SEO / GSC**
- Главная (`/`) проиндексирована с 26.10.2026.
- `/products` проиндексирована 16.11.2026.
- Sitemap на pages.dev Google почти не читает — нормально для shared-домена.

**Метрики (последний полный срез 31.10)**
- Paid sales = 0 (1 free trial = owner test)
- Главный разрыв был: низкий охват + почти нулевые saves → стратегия = list-пины + free/$5 + SEO

---

## 4. SEO-правила пинов + lint (обязательно)

Полный файл: `FOCUS-pinterest-seo-rules.md`.

**Кратко:**
- **pin_title:** основная поисковая фраза **в начале**.
- **description:** keyword-first + польза + мягкий CTA.
- **Hashtags: цель для новых партий 0–2.** Lint в publish.py допускает 0–4 (HASHTAGS_MIN=0, HASHTAGS_MAX=4). Старые строки с 3–4 не бракуются. Не возвращать MIN=3.
- 60–70% пинов на free Starter / $5 Soft Structure.
- List-формат предпочтителен.
- **CSV-формат:** каждое текстовое поле в двойных кавычках, особенно `board` (в названиях есть запятые, напр. «ADHD Holidays, Gifts & Budget»).

**Предпроверка перед отправкой партии (критично):**
1. Сверить **все** title и pin_title новой партии со всем pins.csv (включая status=new и ready). merge_batch.py отклоняет дубли title/description.
2. Локально: `python publish.py --lint` на копии + тестовый merge_batch.py.
3. После Merge pins batch смотреть **batches/_report.md** («принято N, отклонено M»), а не только зелёный статус Actions. Если M>0 — чинить и слать *_fix.csv.
4. Для LINKS fallback патча 20.11 и любых правок publish.py: брать **текущий** файл из репо (main), не локальную устаревшую копию.

Эти правила применяются ко **всем** будущим `pins_batch_*.csv`. Автоматизации Grok обязаны их соблюдать.

---

## 5. Ключевые документы (artifacts + репо)

| Файл | Где | Что |
|------|-----|-----|
| FOCUS-source-of-truth.md | репо root + artifacts | Единый снимок |
| FOCUS-pinterest-seo-rules.md | репо + artifacts | Полные SEO-правила |
| FOCUS-sales-strategy-2026-10-31.md | artifacts | Стратегия продаж |
| FOCUS-claude-note-2026-11-18.md | репо (рядом с 16.11) | Разбор batch_20 reject + фиксы |
| ops/status.md + ops/auto-status.md | **репо** | Живой STATUS / числа |
| publish.py | репо | HASHTAGS_MIN=0, MAX=4; LINKS fallback ещё старый (патч 20.11) |

---

## 6. Роли

- **Grok:** партии пинов (CSV), SEO, push/merge, мониторинг, обновление source-of-truth, Automations. При создании батча — обязательная предпроверка title vs pins.csv + 0–2 hashtags + quoted CSV.
- **Claude:** Metricool + Typefully, external_posts, стратегия/ревью, тесты скриптов.
- **Владелец:** только исключения.

---

## 7. Инцидент 18.11 (batch_20) — выводы для автоматизации

1. Партия написана по SEO (0–2 hashtags) → отклонена старым lint (HASHTAGS_MIN=3). Исправлено в publish.py.
2. 4 title-дубля (темы 516/517/527/528) + 1 description=title + 1 CSV-запятая в board без кавычек.
3. Зелёный Merge ≠ принято 0. Всегда читать _report.md.
4. **Причина:** автоматизация создания батча не синхронизировала lint-конфиг репо и не делала полный title-dedup против pins.csv.  
   **Исправление:** жёсткие правила в §4 + этот source-of-truth; следующие батчи проверять локально перед upload.

---

## 8. Ближайшие действия (приоритет)

1. **19.11** — проверить, что у 532–567 появились images/N.jpg (Daily pins), нет сбоев генерации / квоты Workers AI.
2. **20.11** — LINKS fallback patch в publish.py (приоритет free Starter + $5 Soft Structure). База = текущий main.
3. **22.11** — черновик оптимизации страниц Gumroad.
4. **26.11 10:00 Kyiv** — инструкция: 1 новая доска + 4–6 ручных BF-пинов + снижение авто до 4–6 (итого 8–12).
5. Поддерживать запас info >21 дня.
6. После первых $100 earnings — Publish Starter workflow.

---

## 9. Инструкция для Claude (копировать)

```
Синхронизируй все свои project documents / memory / handoff по FOCUS с файлом FOCUS-source-of-truth.md (актуальная версия от Grok, 18.11.2026 или новее).

Это единый source of truth. 
- Обнови статус pins=560, batch_20_fix принят, intentional rejects удалены.
- Hashtags: цель 0–2 для новых, lint 0–4. Не возвращать MIN=3.
- Предпроверка title vs весь pins.csv обязательна.
- Прочитай FOCUS-claude-note-2026-11-18.md (разбор инцидента).
- Ближайшее: 19.11 images check, 20.11 LINKS, 22.11 Gumroad draft, 26.11 BF board.
- При расхождении приоритет у source-of-truth + живые ops/* в репозитории.
```

---

*Grok обновляет этот файл после значимых изменений. Копия в корне репозитория как `FOCUS-source-of-truth.md`.*
