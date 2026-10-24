# Auto status (ops_report.py) — 2026-10-24 00:40 UTC

## Pinterest (pins.csv)
- Строк 366: new 208, published 86, ready 66, scheduled 6
- Неопубликованных информационных (new+ready): 214; хватит до 2026-11-26; до 2027-01-14 докупить ≈ 369
- Неопубликованных промо (new+ready): 60; хватит до 2026-11-25; до 2027-01-14 докупить ≈ 104
- Запас информационных: 33 дн. → в норме
- lint pins.csv: замечаний нет
- Строк new со сдвинутыми колонками (служебные поля заполнены): 0
- Описаний с фразой-добивкой «small visible step»: 0

## Facebook/X (social.csv)
- S (Facebook, Buffer): ready 20 (без картинки: 0), new 0, scheduled/published 3
- SX (X, Buffer): ready 18 (без картинки: 0), new 0, scheduled/published 5
- M (Facebook, Metricool): ready 40 (без картинки: 20), new 0, scheduled/published 0
  - ОШИБКА: ready без картинки → publish упадёт: M021, M022, M023, M024, M025, M026, M027, M028, M029, M030, M031, M032, M033, M034, M035, M036, M037, M038, M039, M040 (нужно status=new)

## Партии
- Файлов в корне, ждущих слияния: social_batch_2.csv
- Отклонённых строк нет

## Последние запуски Actions
- 10-24T00:40 Ops report: in_progress
- 10-24T00:38 Daily pins: success
- 10-23T23:58 Ops report: success
- 10-23T23:57 Autopilot: success
- 10-23T09:31 Ops report: success
- 10-23T08:46 Ops report: success
- 10-23T08:45 Daily pins: success
- 10-23T07:58 Ops report: success
- 10-23T07:58 Autopilot: success
- 10-23T00:41 Ops report: success
