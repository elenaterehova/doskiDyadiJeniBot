from bot.core.GoogleRepository import *

repo = GoogleRepository(apiWorker=GoogleSheetsAPI('1-NnH2xy84i9SgrZZbsZTjdPDfq4kRywBo047o9yHigM'))

import asyncio
import logging

from aiogram import F, Bot, Router, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboards.admin import admin_keyboard
from bot.keyboards.user import user_keyboard

router = Router()
main_admin_id = 1302324252


class EventRegistration(StatesGroup):
    # add admin
    set_id = State()
    set_name = State()

    #subscribe to the event
    set_user_name = State()
    set_user_phone_number = State()

#     add event
    set_event_title = State()
    set_new_event_title = State()
    set_event_description = State()
    set_event_date = State()


states = EventRegistration()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.set_data(data={})
    user = message.from_user.id
    if repo.is_admin(user):
        await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. '
                                  'Здесь вы можете записаться на мероприятие.',
                             reply_markup=admin_keyboard.admins_start_keyboard())
    else:
        await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. '
                                  'Здесь вы можете записаться на мероприятие.',
                             reply_markup=user_keyboard.user_start_keyboard())

@router.callback_query(F.data.contains('main_state'))
async def main_state(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    user = callback_query.from_user.id
    data = await state.get_data()

    # Проверка на необходимость удаления сообщений
    key = f'deleting_messages_{callback_query.from_user.id}'
    if key in data and data[key] is not None:
        messages_id = data[key]

        for _id in messages_id:
            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=_id)
        del data[key]
        await state.set_data(data=data)
        await asyncio.sleep(delay=0.5)

    # Проверка на необходимость изменения сообщения
    key = f'edit_message_id_{callback_query.from_user.id}'
    edit_messages_id = None
    if key in data and data[key] is not None:
        edit_messages_id = data[key]
        del data[key]
        await state.set_data(data=data)

    key = f'is_editing_{callback_query.from_user.id}'
    data = await state.get_data()
    if key in data:
        del data[key]
        await state.set_data(data=data)

    admin_text = 'Бот для канала Доски дяди Жени. \nЗдесь вы можете записаться на мероприятие.'
    user_text = 'Бот для канала Доски дяди Жени. \nЗдесь вы можете записаться на мероприятие.'
    if repo.is_admin(user):
        if edit_messages_id is not None:
            print(edit_messages_id)
            await bot.edit_message_text(text=admin_text,
                                        chat_id=callback_query.from_user.id,
                                        message_id=edit_messages_id,
                                        reply_markup=admin_keyboard.admins_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=admin_text,
                                   reply_markup=admin_keyboard.admins_start_keyboard())
    else:
        if edit_messages_id is not None:
            await bot.edit_message_text(text=admin_text,
                                        chat_id=callback_query.from_user.id,
                                        message_id=edit_messages_id,
                                        reply_markup=user_keyboard.user_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=user_text,
                                   reply_markup=user_keyboard.user_start_keyboard())
