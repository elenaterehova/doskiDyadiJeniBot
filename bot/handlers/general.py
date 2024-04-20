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

router = Router()
main_admin_id = 1302324252


class EventRegistration(StatesGroup):
    # add admin
    set_id = State()
    set_name = State()



states = EventRegistration()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # if not manager.is_user(info=message.from_user):
    #     manager.add_user(user=User(info=message.from_user))

    if message.from_user.id == 1302324252:
        await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. '
                             'Здесь вы можете записаться на мероприятие.',
                             reply_markup=admin_keyboard.admins_start_keyboard())

    # if main_admin_id is not None and message.from_user.id == main_admin_id:
    #     manager.add_admin(admin=Administrator(info=message.from_user))
    #
    # if manager.is_admin(info=message.from_user):
    #     await message.answer(text=strings.greet.format(name=message.from_user.full_name),
    #                          reply_markup=kb.admins_start_keyboard())
    #     await state.set_state(states.choosing_act_admin)
    #     raise Exception
    # else:
    #     await message.answer(
    #         text=strings.greet.format(name=message.from_user.full_name),
    #         reply_markup=kb.users_start_keyboard()
    #     )
    #     await state.set_state(states.choosing_act)
