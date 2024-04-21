from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def admins_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text='Записаться на мероприятие', callback_data='subscribe_for_the_event')],
        [InlineKeyboardButton(text='Мои мероприятия', callback_data='my_events')],
        [InlineKeyboardButton(text='Добавить мероприятие', callback_data='add_event')],
        [InlineKeyboardButton(text='Показать администраторов', callback_data='show_admins')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def remove_admin_kb(id):
    keyboard = [
        [InlineKeyboardButton(text='Удалить', callback_data=f"remove_admin_{id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def add_admin_kb():
    keyboard = [
        [InlineKeyboardButton(text='Добавить администратора', callback_data='add_admin')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)