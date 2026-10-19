"""FOCUS pins: планирование пинов на СЕГОДНЯ в Pinterest через Buffer (GraphQL API).

Запуск:
  python publish.py              обычный: запланировать в Buffer пины текущего дня (Киев)
  python publish.py --dry-run    ничего не отправлять и не менять, только показать, что было бы сделано
  python publish.py --check      проверка связи: токен, канал, доски, пауза очереди, очередь (только чтение)
  python publish.py --lint       проверка pins.csv (длины, хэштеги, картинки) без обращения к Buffer
  python publish.py --plan [N]   таблица «сколько пинов в день» на N дней вперёд (по умолчанию 45)

Документация Buffer: https://developers.buffer.com  (эндпоинт https://api.buffer.com, Authorization: Bearer <ключ>,
мутация createPost: schedulingType=automatic, mode=customScheduled, dueAt (UTC), assets[].image.url,
metadata.pinterest{title,url,boardServiceId}).
"""
import csv
import json
import os
import random
import sys
import time
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# =====================================================================
#                              КОНФИГ
# =====================================================================
CONFIG = dict(
    # --- Buffer / Pinterest ---
    CHANNEL_ID="6ab95df9ea19ca0bde06b951",          # канал Pinterest @Focus_adhd_planner
    ORG_ID="6ab95d486d34d034827f4193",
    BOARD_INFO="703617210473228341",                # ADHD Tips & Focus Hacks
    BOARD_PROMO="703617210473228343",               # FOCUS – ADHD Planner
    QUEUE_LIMIT=10,                                 # Buffer Free: до 10 запланированных постов на канал

    # --- сколько пинов в день ---
    START_DATE="2026-10-01",                        # день 1; до этой даты ничего не публикуется
    MAX_PER_DAY=10,                                 # жёсткий потолок (и запас под лимит очереди)
    STAGE_DAYS=10,                                  # длина этапа
    STAGE0_BASE=2, STAGE0_PLUS_DAYS=3,              # этап 1: базово 2, в 3 днях из 10 — по 3
    STAGE1_BASE=4, STAGE_STEP=2, PLUS_DAYS=3,       # этап 2: 4, дальше +2 за этап; в 3 днях из 10 — на 1 больше
    DOWN_DAYS=((1, 3), (2, 1)),                     # на максимуме: 3 дня на 1 меньше и 1 день на 2 меньше
    STOCK_DAYS=5,                                   # «склад» картинок на 5 дней вперёд (было 3)

    # --- время (Киев) ---
    WINDOW_START=(8, 0), WINDOW_END=(23, 30),
    MIN_GAP_MIN=40,                                 # минимальный интервал между пинами
    FALLBACK_GAP_MIN=25,                            # если 40 мин не помещается
    LEAD_MIN=20,                                    # при позднем запуске — не ближе чем через N минут от «сейчас»
    HOUR_WEIGHTS={8: 2, 9: 3, 10: 4, 11: 4, 12: 5, 13: 5, 14: 4, 15: 4, 16: 5, 17: 6,
                  18: 7, 19: 8, 20: 9, 21: 9, 22: 7, 23: 3},

    # --- доски ---
    PROMO_MIN_GAP=3,                                # между двумя промо-пинами минимум 3 обычных (до ~1 из 4)

    # --- ссылки: (url, вес) по типу доски. Итого ≈ 70% pages.dev / ≈ 23% dwshkr / ≈ 7% seqen ---
    LINKS={
        "info": [("https://focus-mini.pages.dev/", 74), ("https://vivatic.gumroad.com/l/dwshkr", 26)],
        "promo": [("https://focus-mini.pages.dev/", 45), ("https://vivatic.gumroad.com/l/seqen", 55)],
    },

    # --- проверка текста ---
    DESC_MIN=300, DESC_MAX=450, DESC_HARD_MAX=500,  # 500 — лимит Pinterest
    TITLE_MAX=100,
    HASHTAGS_MIN=3, HASHTAGS_MAX=4,
)

REPO = os.environ.get("GITHUB_REPOSITORY") or "vivaticvv-cyber/focus-pins"
BRANCH = os.environ.get("GITHUB_REF_NAME") or "main"
API_URL = "https://api.buffer.com"
FIELDS = ["id", "topic", "title", "pin_title", "description", "board", "status", "scene_prompt",
          "style", "layout", "link", "scheduled_at", "buffer_post_id"]


def cfg(name):
    """Значение конфига; START_DATE, MAX_PER_DAY, STOCK_DAYS можно переопределить переменной окружения."""
    if name in ("START_DATE", "MAX_PER_DAY", "STOCK_DAYS"):
        v = (os.environ.get(name) or "").strip()
        if v:
            return v if name == "START_DATE" else int(v)
    return CONFIG[name]
