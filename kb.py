from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
menu = [
    [InlineKeyboardButton(text="Время доставки",
                          callback_data="asdsad"),
    InlineKeyboardButton(text="Не привезли заказ", callback_data="generate_image")],
    [InlineKeyboardButton(text="Товар повреждён", callback_data="buy_tokens"),
    InlineKeyboardButton(text="Испорченный продукт", callback_data="balance")],
    [InlineKeyboardButton(text="🔎 Другой вопрос", callback_data="generate_response")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])