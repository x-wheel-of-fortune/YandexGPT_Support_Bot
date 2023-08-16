from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Текстовый режим",
                                 callback_data="text_response"),
            InlineKeyboardButton(text="Голосовой режим",
                                 callback_data="audio_response")
        ],
    ],
)

exit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅️ Вопрос решён"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

choice_of_answer_order_damaged = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Товар"),
            KeyboardButton(text="Купон"),
            KeyboardButton(text="Карта"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
