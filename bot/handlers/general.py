from bot.core.GoogleRepository import *

repo = GoogleRepository(apiWorker=GoogleSheetsAPI('1-NnH2xy84i9SgrZZbsZTjdPDfq4kRywBo047o9yHigM'))

import asyncio
import logging

from aiogram import F, Bot, Router
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
    repo.apiWorker.delete_sheet(sheet=1)
    # repo.apiWorker.add_sheet(1, '123', ['123', '123', '123'])
    # user = message.from_user.id
    # if repo.is_admin(user):
    #     await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. '
    #                               'Здесь вы можете записаться на мероприятие.',
    #                          reply_markup=admin_keyboard.admins_start_keyboard())
    # else:
    #     await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. '
    #                               'Здесь вы можете записаться на мероприятие.',
    #                          reply_markup=user_keyboard.user_start_keyboard())
