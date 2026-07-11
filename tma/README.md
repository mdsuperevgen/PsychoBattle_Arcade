# PsychoBattle Arcade — Telegram Mini App

Игра портирована на JavaScript/Canvas для запуска в Telegram Mini App.

## GitHub Pages (хостинг)

Mini App хостится бесплатно на GitHub Pages:

**URL:** `https://mdsuperevgen.github.io/PsychoBattle_Arcade/tma/`

## Настройка через BotFather

1. Открой [@BotFather](https://t.me/botfather)
2. Напиши `/mybots` → выбери `PsychoBattle Arcade` → **Bot Settings** → **Menu Button**
3. Установи URL: `https://mdsuperevgen.github.io/PsychoBattle_Arcade/tma/`
4. Текст кнопки: `🧠 Играть`

Или через **Configure Mini App**:
- **Bot Settings** → **Configure Mini App** → включи Mini App
- Установи URL: `https://mdsuperevgen.github.io/PsychoBattle_Arcade/tma/`

После этого в чате с ботом появится кнопка **Запустить** или кнопка в меню.

## Управление

| Действие | Управление |
|----------|-----------|
| Движение | Клавиши ← → / A D / тач |
| Стрельба | Пробел / тач в левом нижнем углу |
| Бомба | Клавиша B / кнопка справа |
| Барьер | Клавиша E / кнопка справа |
| Пауза | P |

## Сборка

Один файл `index.html` — всё включено. Открывается в любом браузере.

## Разработка

```bash
# Открыть локально
cd tma
python -m http.server 8000
# Открыть http://localhost:8000
```
