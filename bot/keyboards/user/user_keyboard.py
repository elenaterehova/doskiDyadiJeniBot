from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def user_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='Записаться на мероприятие', callback_data='user_subscribe_for_the_event')],
        [InlineKeyboardButton(text='Мои мероприятия', callback_data='user_my_events')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

