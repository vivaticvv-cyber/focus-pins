# FOCUS ops status

**Updated:** 2026-10-20 22:20 Kyiv (Grok)

## STATUS: DONE

Конвейер стабилен. Следующая осознанная работа — пополнение stock / social_batch по `ops/auto-status.md` или чекпоинт продаж 31.10.

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

- Autopilot **#22** failure (SyntaxError social_publish) — **исправлено** restore 56a4622+PATTERN
- Autopilot **#23–#24** success (X SX006 в Buffer; heal_social 10→new; картинки S021–025, SX021)

### Grok Automations (не GH)
| Имя | Расписание Киев |
|-----|-----------------|
| FOCUS daily ops check | ежедневно **4:30** |
| FOCUS batch continue | каждый час **4:45–7:00** |

Решение 20.10: **не сдвигать на 3:30** — текущего окна хватает при коротких зелёных прогонах.

### Сделано 20.10 (Grok + Claude help-2/3)
- `social_publish.py` restored; `heal_social` в autopilot_prep
- merge_batch/social: shape_issue, per-row reject, **без** auto-pad текста
- pins_patch_5–8: pad 47→0; promo links 267/284/289/294/299/304/309 в колонке `link`
- ops_report + metrics.md; check-code.yml; убраны one-shot restore workflows
- Корень очищен от leftover patches

### Permanent rules (кратко)
1. Скрипты не меняют авторский текст (нет auto-pad)
2. Плохая строка отклоняется отдельно
3. Нет one-shot workflows, перезаписывающих исходники
4. Backup SHA перед правкой важных скриптов; только улучшение
5. Facebook Buffer = каждый 3-й день (PATTERN); X каждый день кроме Typefully
6. CSV: 13 колонок, **все текстовые поля в кавычках**, куски ≤10 строк
7. Сцены без laptop/screen/phone/hand/person/face…
8. Запас смотреть в `ops/auto-status.md`, не по числу ready-картинок
9. social картинки **отдельно** от Pinterest: FB 1080×1350 (4:5), X 1600×900
10. Metricool / Typefully / external_posts — зона Claude

### Next (без участия владельца)
1. Ночной Daily + утренний Autopilot по cron
2. При info runway < 14 дн. — новая pins_batch (info)
3. При падении social ready — social_batch + stock
4. 25.10 / 31.10 — владелец заполняет metrics.md
