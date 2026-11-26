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
import math
import re
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
    CHANNEL_ID="6aeb6ecfe29c69a17160459d",          # канал Pinterest @Focus_adhd_planner (reconnected 04.11)
    ORG_ID="6ab95d486d34d034827f4193",
    # Доски: название в CSV → serviceId (из Buffer get_channel, 05.11.2026)
    BOARDS={
        "ADHD Tips & Focus Hacks":          "703617210473228341",  # info
        "FOCUS – ADHD Planner":             "703617210473228343",  # promo
        "ADHD Digital Planner & GoodNotes": "703617210473241211",  # promo
        "ADHD Holidays, Gifts & Budget":    "703617210473241209",  # info
        "ADHD Home & Low-Energy Chores":    "703617210473241208",  # info
        "ADHD Morning & Evening Routines":  "703617210473241205",  # info
        "ADHD New Year Reset (gentle)":     "703617210473241212",  # info
        "ADHD Overwhelm & Reset Tools":     "703617210473241206",  # info
        "ADHD Work & Study Focus":          "703617210473241207",  # info
        "Free ADHD Printables (Undated)":   "703617210473241210",  # promo
    },
    # fallback (если название доски из CSV не найдено)
    BOARD_INFO="703617210473228341",
    BOARD_PROMO="703617210473228343",
    QUEUE_LIMIT=10,                                 # Buffer Free: до 10 запланированных постов на канал

    # --- распределение по тематическим доскам (с 8.11.2026) ---
    NEW_BOARDS=(
        "ADHD Digital Planner & GoodNotes", "ADHD Holidays, Gifts & Budget", "ADHD Home & Low-Energy Chores",
        "ADHD Morning & Evening Routines", "ADHD New Year Reset (gentle)", "ADHD Overwhelm & Reset Tools",
        "ADHD Work & Study Focus", "Free ADHD Printables (Undated)",
    ),
    NEW_BOARD_SHARE=0.5,
    BF_WINDOW=("2026-11-08", "2026-11-30"),
    BF_GENERATE_DAYS_BEFORE=3,
    BF_SOFT_END="2026-11-15",
    BF_SOFT_MAX=2,
    BF_WARMUP=5, BF_WARMUP_END="2026-11-25",
    NEW_PROMO_SHARE=0.6,

    # --- сколько пинов в день ---
    START_DATE="2026-10-01",
    MAX_PER_DAY=6,                                  # с 27.11.2026: 6/день для роста показов (было 10)
    STAGE_DAYS=10,
    STAGE0_BASE=2, STAGE0_PLUS_DAYS=3,
    STAGE1_BASE=4, STAGE_STEP=2, PLUS_DAYS=3,
    DOWN_DAYS=((1, 3), (2, 1)),
    STOCK_DAYS=5,

    # --- время (Киев) ---
    WINDOW_START=(8, 0), WINDOW_END=(23, 30),
    MIN_GAP_MIN=40,
    FALLBACK_GAP_MIN=25,
    LEAD_MIN=20,
    HOUR_WEIGHTS={8: 2, 9: 3, 10: 4, 11: 4, 12: 5, 13: 5, 14: 4, 15: 4, 16: 5, 17: 6,
                  18: 7, 19: 8, 20: 9, 21: 9, 22: 7, 23: 3},

    PROMO_MIN_GAP=3,

    LINKS={
        "info": [
            ("https://vivatic.gumroad.com/l/focus-starter", 55),
            ("https://vivatic.gumroad.com/l/soft-structure-printable", 25),
            ("https://focus-mini.pages.dev/", 12),
            ("https://vivatic.gumroad.com/l/dwshkr", 8),
        ],
        "promo": [
            ("https://vivatic.gumroad.com/l/focus-starter", 40),
            ("https://vivatic.gumroad.com/l/soft-structure-printable", 40),
            ("https://vivatic.gumroad.com/l/seqen", 12),
            ("https://focus-mini.pages.dev/", 8),
        ],
    },

    DESC_MIN=300, DESC_MAX=450, DESC_HARD_MAX=500,
    TITLE_MAX=100,
    HASHTAGS_MIN=0, HASHTAGS_MAX=4,
)
