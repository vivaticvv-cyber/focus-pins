# FOCUS — Source of Truth (единый актуальный снимок проекта)

**Обновлено:** 21 ноября 2026, ~11:15 EET (Grok)  
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

**LINKS fallback в publish.py (с 20.11.2026):**  
- info: Starter 55 / Soft Structure $5 25 / pages.dev 12 / dwshkr 8  
- promo: Starter 40 / Soft Structure $5 40 / seqen 12 / pages.dev 8  
Явная ссылка в CSV всегда побеждает fallback.

Workflows (email follow-up): Starter workflow в DRAFT (нужно ≥$100 earnings + payout, чтобы Publish). Mini deferred.

---

## 3. Текущий статус (21.11.2026)

**Pinterest / pins.csv**
- Строк: **560**
- Статусы (ops/auto-status 21.11 03:13 UTC): published 312, new 170, ready 68, scheduled 10
- Неопубликованных info (new+ready): 163 → хватит до ~14.12 (≈23 дн., норма)
- Промо (new+ready): 75 → хватит до ~27.12
- Next batch due: **2026-11-25**
- Root чист, 0 rejects, lint без замечаний
- Daily #115 + Autopilot #108 + Ops report зелёные (21.11)
- CHANNEL_ID: `6aeb6ecfe29c69a17160459d`
- 10 досок, altText включён, NEW_BOARD_SHARE=0.5
- HASHTAGS_MIN=0, HASHTAGS_MAX=4 (не менять)

**BF30 (Black Friday soft)**
- Soft: 8–15.11 (max 2) — завершён
- Warm: 16–25.11 (max 5 всего) — сейчас (опубликовано 5 BF-пинов)
- Active: 26–30.11
- Тон: код + даты вместе, без FOMO
- **Date-filter в publish.py ЕСТЬ** (BF_WINDOW 08–30.11, bf_allowed(), bf_cum() с фазами soft→warm→active). Документы handoff/brief раньше ошибочно писали «нет».
- Окно рекламы до 30.11; акция на Gumroad до 01.12 10:00 — нормально.

**SEO / GSC**
- Главная (`/`) проиндексирована с 26.10.2026.
- `/products` проиндексирована 16.11.2026.
- Sitemap на pages.dev Google почти не читает — нормально для shared-домена.

**Метрики (последний полный срез 31.10)**
- Paid sales = 0 (1 free trial = owner test)
- Главный разрыв был: низкий охват + почти нулевые saves → стратегия = list-пины + free/$5 + SEO

**Очередь / приоритет (проверка 21.11)**
- Партия ids ≥529 (SEO free Starter / $5 от 18.11) стоит в хвосте: choose_pins и generation_order берут по возрастанию id (после приоритета новых досок). Выйдут ближе к середине декабря.
- Product-mockup в неопубликованной очереди почти нет (цель 40–50 % в следующей партии).
- На 26.11: Daily cron 22:17 UTC 25.11 уже планирует пины на 26.11. Снижение авто до 4–6 нужно внести до этого момента (MAX_PER_DAY variable или ручное удаление лишних из Buffer + возврат status=ready).

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
4. Для любых правок publish.py: брать **текущий** файл из репо (main), не локальную устаревшую копию.

Эти правила применяются ко **всем** будущим `pins_batch_*.csv`. Автоматизации Grok обязаны их соблюдать.

---

## 5. Ключевые документы (artifacts + репо)

| Файл | Где | Что |
|------|-----|-----|
| FOCUS-source-of-truth.md | репо root + artifacts | Единый снимок |
| FOCUS-pinterest-seo-rules.md | репо + artifacts | Полные SEO-правила |
| FOCUS-sales-strategy-2026-10-31.md | artifacts | Стратегия продаж |
| FOCUS-claude-note-2026-11-18.md | репо | Разбор batch_20 reject + фиксы |
| FOCUS-claude-note-2026-11-21.md | artifacts / рядом с 18.11 | Проверка очереди, product-mockup, 26.11, BF-filter |
| ops/status.md + ops/auto-status.md | **репо** | Живой STATUS / числа |
| publish.py | репо | HASHTAGS_MIN=0, MAX=4; LINKS fallback = Starter+$5 (с 20.11); BF date-filter live |

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

1. **20.11** — LINKS fallback patch в publish.py (DONE).
2. **22.11** — черновик оптимизации страниц Gumroad (Grok).
3. **25.11** — партия ≥30–40 пинов: 40–50 % product-mockup, 60–70 % free Starter / $5, сильные Free CTA, 0–2 hashtags, title-dedup.
4. **25.11 вечер (до 22:17 UTC)** — снизить авто-пины на 26.11 до 4–6 (MAX_PER_DAY variable или удаление лишних из Buffer после планирования + status=ready).
5. **26.11 10:00 Kyiv** — инструкция владельцу: 1 новая тематическая доска + 4–6 ручных BF-пинов (итого 8–12). Доску не удалять.
6. Поддерживать запас info >21 дня.
7. После первых $100 earnings — Publish Starter workflow.

---

## 9. Инструкция для Claude (копировать)

```
Синхронизируй все свои project documents / memory / handoff по FOCUS с файлом FOCUS-source-of-truth.md (актуальная версия от Grok, 21.11.2026 или новее).

Это единый source of truth. 
- Статус 21.11: pins=560, stock 23d, published 312 / new 170 / ready 68 / scheduled 10. Daily+Autopilot+Ops green.
- LINKS fallback live (Starter+$5).
- BF date-filter в publish.py УЖЕ ЕСТЬ (BF_WINDOW, bf_allowed, bf_cum). Старые handoff/brief ошибочно писали «нет».
- Hashtags: цель 0–2 для новых, lint 0–4. Не возвращать MIN=3.
- Предпроверка title vs весь pins.csv обязательна.
- Партия ≥529 в хвосте очереди (по id). Product-mockup почти нет — в партии 25.11 нужно 40–50 %.
- 26.11: риск, что Daily 22:17 UTC 25.11 уже запланирует полный день. Снижение до 4–6 нужно до этого.
- Прочитай FOCUS-claude-note-2026-11-21.md (если есть в репо/artifacts).
- Ближайшее: 22.11 Gumroad draft, 25.11 batch + снижение, 26.11 BF board.
- При расхождении приоритет у source-of-truth + живые ops/* в репозитории.
```

---

*Grok обновляет этот файл после значимых изменений. Копия в корне репозитория как `FOCUS-source-of-truth.md`.*
