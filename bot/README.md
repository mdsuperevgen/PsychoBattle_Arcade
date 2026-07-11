# PsychoBattle Arcade — Telegram Bot

Простой Telegram бот для демонстрации игры **PsychoBattle Arcade**. Отправляет описание игры, ссылку на GitHub и скриншоты.

## Команды

- `/start` — Приветствие и описание игры
- `/play` — Инструкция, как начать играть
- `/help` — Справка

## Запуск

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Установите токен бота
set BOT_TOKEN=your_bot_token_here  # Windows
# или
export BOT_TOKEN=your_bot_token_here  # Linux/Mac

python bot.py
```

## Где взять токен

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен
