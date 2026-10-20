"""FOCUS pins v3: разнообразные иллюстрации FLUX.2 klein 4B + разные раскладки заголовков + «склад» на 2–3 дня.

Источники картинок: Cloudflare Workers AI (основной) -> HF Space (резерв, без повторов).
Режимы:
  python generate.py          обычный: докручивает «склад» — держит готовые картинки (status=ready)
                              на STOCK_DAYS дней вперёд по плану publish.py; строки new -> images/N.jpg, status=ready
                              (в складе считаются только ИНФОРМАЦИОННЫЕ пины; продуктовые делает pinterest_product.py)
  python generate.py --test   первые 3 строки pins.csv -> test/ (pins.csv не меняется)
  python generate.py --demo   по одной картинке на КАЖДЫЙ стиль -> test/demo_*.jpg + contact_sheet.jpg
Переменные окружения: PINS_PER_RUN (принудительно сделать ровно N картинок), GEN_MAX_PER_RUN (потолок за прогон, 12),
STOCK_DAYS (3), START_DATE, HF_MAX_PER_RUN (1), CF_GUIDANCE.
Необязательные колонки pins.csv: pin_title, style (ключ стиля), layout (ключ раскладки).
"""
