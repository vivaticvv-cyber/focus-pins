"""FOCUS pins: планирование пинов на СЕГОДНЯ в Pinterest через Buffer (GraphQL API).

Запуск:
  python publish.py              обычный: запланировать в Buffer пины текущего дня (Киев)
  python publish.py --dry-run    ничего не отправлять и не менять, только показать, что было бы сделано
  python publish.py --check      проверка связи: токен, канал, доски, пауза очереди, очередь (только чтение)
  python publish.py --lint       проверка pins.csv (длины, хэштеги, картинки) без обращения к Buffer
  python publish.py --plan [N]   таблица «сколько пинов в день» на N дней вперёд (по умолчанию 45)
"""
