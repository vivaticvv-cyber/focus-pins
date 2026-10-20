# FOCUS ops status

**Updated:** 2026-10-20 23:32 Kyiv (Grok)

## STATUS: DONE

Конвейер стабилен. Продуктовые пины теперь полностью автоматизированы (без Claude).

### Success criterion
- **Метрика:** продажи Gumroad. Сейчас **0**.
- Контроль: **25.10** (промежуточный) и **31.10.2026**. Таблица: `ops/metrics.md` (заполняет владелец).
- Правило 01.11: нет трафика → источники; трафик без кликов на товар → ссылки/посадка; визиты без покупок → страница/цена/доверие.

### Current numbers (сверка с pins.csv / social.csv / auto-status)
- pins.csv: **326** (new 196, ready 63, scheduled 2, published 65)
- Pad-фраза: **0** | Shifted columns: **0** | lint: чисто
- Info runway ~ **34 дн.** (до ~23.11); promo ~ до 17.11
- social: FB Buffer ready 21; X ready 16 + new 4; Metricool ready 20; **ready без картинки: 0**
- Корень: партий/патчей нет

### GitHub Actions (факт)
| Workflow | Cron UTC | Киев (EEST) |
|----------|----------|-------------|
| Daily | 22:17, 03:30 | 01:17, 06:30 |
| Autopilot | 21:40, 02:55 | 00:40, 05:55 |
| Ops report | 04:40 | 07:40 |

- Autopilot **#22** failure (SyntaxError social_publish) — **исправлено**
- Autopilot **#23–#24** success

### Grok Automations (не GH)
| Имя | Расписание Киев |
|-----|-----------------|
| FOCUS daily ops check | ежедневно **4:30** |
| FOCUS batch continue | каждый час **4:45–7:00** |

### Сделано 20.10 (Grok + Claude help-2/3/4)
- help-2/3: social_publish, heal_social, merges без auto-pad, pad→0, links, metrics.md
- **help-4 COMPLETE:** `product_pins.py` + `product_specs.csv` (34 specs) + skip в `generate.py` + вызов в `autopilot_prep.py`
- Продуктовые пины теперь рисует Autopilot автоматически (без Claude и без нейросети)

### График пополнения (help-4, чтобы runway ≥ 14 дн.)
| к дате | info дописано | promo дописано |
|--------|---------------|----------------|
| 10.11  | 14            | 16             |
| 17.11  | 66            | 30             |
| 24.11  | 117           | 45             |
| 01.12  | 169           | 59             |

Ритм: ~40 info + 12 promo в неделю (файлами по 10 строк).

### Permanent rules (кратко)
1. Скрипты не меняют авторский текст (нет auto-pad)
2. Плохая строка отклоняется отдельно
3. Нет one-shot workflows, перезаписывающих исходники
4. Backup SHA перед правкой важных скриптов; только улучшение
5. Facebook Buffer = каждый 3-й день (PATTERN); X каждый день кроме Typefully
6. CSV: 13 колонок, **все текстовые поля в кавычках**, куски ≤10 строк
7. Сцены без laptop/screen/phone/hand/person/face…
8. Запас смотреть в `ops/auto-status.md`
9. social картинки **отдельно** от Pinterest: FB 1080×1350 (4:5), X 1600×900
10. Metricool / Typefully / external_posts — зона Claude
11. **Продуктовые пины:** scene_prompt = `product pin (pinterest_product.py)` + строка в `product_specs.csv` → рисует `product_pins.py`

### Next (без участия владельца)
1. Ночной Daily + утренний Autopilot по cron
2. При info runway < 14 дн. — pins_batch (info)
3. При падении social ready — social_batch
4. 25.10 / 31.10 — владелец заполняет metrics.md
5. Промо начинать уже сейчас (цель ≥16 к 10.11, половина — продуктовые)
