from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def make_start_keyboard() -> InlineKeyboardMarkup:
    start_kb = InlineKeyboardMarkup()
    start_kb.add(
        InlineKeyboardButton('OpenWeatherMap', callback_data='owm'),
        InlineKeyboardButton('Gismeteo', callback_data='gismeteo')
    )
    return start_kb


def make_back_button_keyboard(text='/start') -> InlineKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text))
    return kb
