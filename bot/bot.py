"""
PsychoBattle Arcade — Telegram Bot.

Простой бот, который рассказывает об игре, показывает ссылку на GitHub
и поддерживает базовые команды.

Перед запуском установите переменную окружения BOT_TOKEN.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

GITHUB_URL = "https://github.com/your-username/PsychoBattle_Arcade"
GAME_NAME = "🧠 Психо-Бой: Битва со Страхами"

GAME_DESCRIPTION = """
🎮 *{name}*

2D аркада на Python, где ты сражаешься со своими страхами!

🔹 10 тематических уровней (Зоофобии, Гидрофобии, Технофобии и др.)
🔹 Уникальные боссы на каждом уровне
🔹 Система бонусов: щит, лазер, бомба, помощники
🔹 Комбо-система и 17 достижений
🔹 3 уровня сложности
🔹 Адаптивное управление (клавиатура + тач)
""".format(name=GAME_NAME)

HOW_TO_PLAY = """
🖥 *Как начать играть:*

1. Скачай репозиторий с GitHub
2. Установи Python 3.10+
3. Установи зависимости: `pip install -r requirements.txt`
4. Запусти: `python main.py`

*Управление:*
← → / A D — движение
Пробел / ЛКМ — стрельба
B — бомба
E — барьер
P — пауза
ESC — меню
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветствие и клавиатуру."""
    keyboard = [
        [InlineKeyboardButton("ℹ️ Об игре", callback_data="about")],
        [InlineKeyboardButton("🎮 Как играть", callback_data="howto")],
        [InlineKeyboardButton("📦 GitHub", url=GITHUB_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 *Добро пожаловать в {GAME_NAME}!*\n\n"
        f"Твой мозг — главное оружие. Сражайся со страхами, "
        f"побеждай боссов и становись сильнее!",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет инструкцию по запуску."""
    keyboard = [[InlineKeyboardButton("📦 Открыть на GitHub", url=GITHUB_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        HOW_TO_PLAY,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет список команд."""
    await update.message.reply_text(
        "📋 *Команды:*\n\n"
        "/start — Приветствие\n"
        "/play — Как начать играть\n"
        "/help — Это сообщение",
        parse_mode="Markdown",
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на инлайн-кнопки."""
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        keyboard = [[InlineKeyboardButton("🎮 Как играть", callback_data="howto")]]
        await query.edit_message_text(
            GAME_DESCRIPTION,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
    elif query.data == "howto":
        keyboard = [[InlineKeyboardButton("📦 Открыть на GitHub", url=GITHUB_URL)]]
        await query.edit_message_text(
            HOW_TO_PLAY,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


def main() -> None:
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN не установлен! Задайте переменную окружения BOT_TOKEN.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
