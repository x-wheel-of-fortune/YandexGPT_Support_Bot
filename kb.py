from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)


menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Текстовый режим", callback_data="text_response"),
            InlineKeyboardButton(text="Голосовой режим", callback_data="audio_response"),
        ],
    ],
)

exit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="◀️ Выйти в меню"),
        ],
    ],
    resize_keyboard=True,
)

iexit_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu"),
        ],
    ],
)
