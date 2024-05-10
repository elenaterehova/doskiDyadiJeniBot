import re

from bot.core.GoogleRepository import *
from bot.core.Constants import spreadsheet
from bot.keyboards.user.user_keyboard import user_start_keyboard

repo = GoogleRepository(apiWorker=GoogleSheetsAPI(spreadsheet))

import asyncio
import logging

from aiogram import F, Bot, Router, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter, CommandObject, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboards.admin import admin_keyboard
from bot.keyboards.user import user_keyboard

router = Router()


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

    # edit event
    edit_event_title = State()
    edit_event_description = State()
    edit_event_date = State()


states = EventRegistration()


@router.message(CommandStart(deep_link=deeplink, magic=F.args.regexp(re.compile(r'register_event_(\d+)'))))
async def register_handler(message: Message, state: FSMContext, command: CommandObject):
    args = command.args
    event_id = command.args.split("_")[2]
    event_list = repo.get_events()
    user_id = str(message.from_user.id)
    for e in event_list:
        if event_id == e.id:
            event_title = e.title
    if repo.is_subscribed(event_id, user_id):
        await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. \n'
                                  f'Чтобы зарегистрироваться на мероприятие "{event_title}", нажмите на кнопку ниже.',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[[InlineKeyboardButton(text='Вы уже записаны на это мероприятие.',
                                                                        callback_data=f"already_subscribed")]],
                                 resize_keyboard=True,
                                 one_time_keyboard=True))
    else:
        await message.answer(text='Здравствуйте, это бот для канала Доски дяди Жени. \n'
                                  f'Чтобы зарегистрироваться на мероприятие "{event_title}", нажмите на кнопку ниже.',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[[InlineKeyboardButton(text='Записаться на мероприятие',
                                                                        callback_data=f"event_id:{event_id}")]],
                                 resize_keyboard=True,
                                 one_time_keyboard=True))


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
            await bot.send_message(text=admin_text,
                                   chat_id=callback_query.from_user.id,
                                   reply_markup=admin_keyboard.admins_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=admin_text,
                                   reply_markup=admin_keyboard.admins_start_keyboard())
    else:
        if edit_messages_id is not None:
            await bot.send_message(text=admin_text,
                                   chat_id=callback_query.from_user.id,
                                   reply_markup=user_keyboard.user_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=user_text,
                                   reply_markup=user_keyboard.user_start_keyboard())


# Мероприятие выбрано, пользователь вводит свое имя
@router.callback_query(F.data.contains("event_id"))
async def event_chosen(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        event_id = callback_query.data.split(':')[1]
        print(event_id)
        await state.set_data({'event_id': event_id, 'user_name': ''})
        await bot.send_message(chat_id=callback_query.from_user.id, text="Введите ваше ФИО:")
        await state.set_state(states.set_user_name)
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


# Имя введено, пользователь вводит номер телефона
@router.message(states.set_user_name)
async def user_name_set(message: Message, bot: Bot, state: FSMContext):
    try:
        fio_pattern = re.compile(
            r'^(([А-Яа-яЁё]+)\-?([А-Яа-яЁё]+))\ (([А-Яа-яЁё]+)\-?([А-Яа-яЁё]+))(\ (([А-Яа-яЁё]+)\-?([А-Яа-яЁё]+)))?$')
        user_name = message.text
        if fio_pattern.match(str(user_name)):
            await state.update_data({'user_name': user_name})
            await bot.send_message(chat_id=message.from_user.id, text="Введите свой номер телефона:")
            await state.set_state(states.set_user_phone_number)
        else:
            await bot.send_message(chat_id=message.from_user.id, text="ФИО введено некорректно. Попробуйте снова.")
            await state.set_state(states.set_user_name)
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


# Номер телефона введен, данные сохраняются в таблицу
@router.message(states.set_user_phone_number)
async def user_phone_number_set(message: Message, bot: Bot, state: FSMContext):
    try:
        data = await state.get_data()
        phone_pattern = re.compile(
            r'^((\+7|7|8)+(\ )?)?(\(?[0-9]{3}\)?)(\ |-)?[0-9]{3}(\ |-)?[0-9]{2}(\ |-)?[0-9]{2}$')
        if phone_pattern.match(message.text) is None:
            await bot.send_message(chat_id=message.from_user.id, text="Некорректный номер телефона. Попробуйте снова.")
            await state.set_state(states.set_user_phone_number)
            return

        id = message.from_user.id
        name = data['user_name']
        user_phone_number = message.text
        telegram_link = message.from_user.username
        event = data['event_id']

        response = repo.subscribe_to_the_event(event_id=event, user=UserModel(user_id=id,
                                                                              name=name,
                                                                              phone_number=user_phone_number,
                                                                              telegram_link=telegram_link))
        if response['subscribed']:
            if repo.is_admin(id):
                await message.answer(text=f'Вы успешно записаны на мероприятие.', reply_markup=admin_keyboard.admins_start_keyboard())
            else:
                await message.answer(text=f'Вы успешно записаны на мероприятие.',
                                     reply_markup=user_start_keyboard())
        else:
            await message.answer(text=f"Ошибка записи на мероприятие: {response['message']}",
                                 reply_markup=user_start_keyboard())

        await state.clear()
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))

@router.message(F.text, StateFilter(None))
async def text_message_handler(message: Message, bot: Bot, state: FSMContext):
    try:
        user = message.from_user.id
        if repo.is_admin(user):
            await bot.send_message(chat_id=message.from_user.id, text='Это бот для канала Доски дяди Жени. '
                                                                      'Здесь вы можете записаться на мероприятие.',
                                   reply_markup=admin_keyboard.admins_start_keyboard())
        else:
            await bot.send_message(chat_id=message.from_user.id, text='Это бот для канала Доски дяди Жени. '
                                                                      'Здесь вы можете записаться на мероприятие.',
                                   reply_markup=user_start_keyboard())
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))