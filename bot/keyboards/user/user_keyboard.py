from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def user_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='Записаться на мероприятие', callback_data='user_subscribe_for_the_event')],
        [InlineKeyboardButton(text='Мои мероприятия', callback_data='user_my_events')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def user_unsub_or_home_button():
    keyboard = [
        [InlineKeyboardButton(text='Отписаться от мероприятия', callback_data='unsub_from_event')],
        [InlineKeyboardButton(text='Главная', callback_data='user_main_state')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def user_unsubscribe():
    keyboard = [
        [InlineKeyboardButton(text='Отписаться', callback_data='user_unsubscribe')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)