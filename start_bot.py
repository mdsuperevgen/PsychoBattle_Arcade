"""
PsychoBattle Arcade — Telegram Bot entry point.

Запускает бота из bot/bot.py.
Используется для деплоя на Bothost.
"""

import sys
import os

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.bot import main

if __name__ == "__main__":
    main()
