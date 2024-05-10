import re

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *
from bot.keyboards.user.user_keyboard import *

user_router = Router()


@user_router.callback_query(F.data.contains('user_subscribe_for_the_event'))
async def subscribe_for_the_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        event_list = repo.get_events()
        user_id = str(callback_query.from_user.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text='Список мероприятий: ')
        for event in event_list:
            # проверка на is_subscribed. Если возвращает True, месседж будет другой
            if repo.is_subscribed(event.id, user_id):
                await bot.send_message(chat_id=callback_query.from_user.id,
                                       text=f"<u><b>{event.title}</b></u>\n\n"
                                            f"{event.description}\n\n"
                                            f"{event.date}",
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=InlineKeyboardMarkup(
                                           inline_keyboard=[[InlineKeyboardButton(text='Вы уже записаны.',
                                                                                  callback_data=f"already_subscribed")]],
                                           resize_keyboard=True,
                                           one_time_keyboard=True))
            else:
                await bot.send_message(chat_id=callback_query.from_user.id,
                                       text=f"<u><b>{event.title}</b></u>\n\n"
                                            f"{event.description}\n\n"
                                            f"{event.date}",
                                       reply_markup=InlineKeyboardMarkup(
                                           inline_keyboard=[[InlineKeyboardButton(text='Записаться сюда',
                                                                                  callback_data=f"event_id:{event.id}")]],
                                           resize_keyboard=True,
                                           one_time_keyboard=True))

    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.callback_query(F.data == "already_subscribed")
async def already_subscribe_disable_button(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    pass


@user_router.callback_query(F.data.contains('my_events'))
async def my_events_list_admin(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await my_events_list(callback_query, bot, state)
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.callback_query(F.data.contains('user_my_events'))
async def my_events_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user = str(callback_query.from_user.id)
        events = repo.get_subscribed_events(user)
        message_id = callback_query.message.message_id
        await bot.send_message(text='Получение всех мероприятий, на которые вы записаны...',
                                    chat_id=callback_query.from_user.id)
        if len(events) == 0:
            message = "Вы не записаны ни на одно мероприятие."
            await bot.send_message(text=message, chat_id=callback_query.from_user.id,
                                        reply_markup=user_start_keyboard())
        else:
            message = "Список мероприятий, на которые вы записаны: \n\n"
            for e in events:
                message += f"Название: <u><b>{e.title}</b></u>\nОписание: {e.description}\nДата: {e.date}\n\n"
            await bot.send_message(chat_id=callback_query.from_user.id, text=message, parse_mode=ParseMode.HTML,
                                        reply_markup=user_unsub_or_home_button())
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.callback_query(F.data.contains('unsub_from_event'))
async def unsub_from_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Выберите мероприятие, от которого хотите отписаться")
        user = str(callback_query.from_user.id)
        events = repo.get_subscribed_events(user)
        messages_id_list = []
        for e in events:
            message = await bot.send_message(chat_id=callback_query.from_user.id,
                                             text=f"Название: <u><b>{e.title}</b></u>\nОписание: {e.description}\nДата: {e.date}\n\n",
                                             parse_mode=ParseMode.HTML,
                                             reply_markup=InlineKeyboardMarkup(
                                                 inline_keyboard=[[InlineKeyboardButton(text='Отписаться',
                                                                                        callback_data=f"user_unsub_event:{e.id}")]],
                                                 resize_keyboard=True,
                                                 one_time_keyboard=True))
            messages_id_list.append(message.message_id)
        await state.set_data({'messages_id_list': messages_id_list})
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.callback_query(F.data.contains('user_unsub_event'))
async def user_unsubscribe(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        event_id = callback_query.data.split(':')[1]
        response = repo.unsubscribe_from_event(event_id=event_id, user_id=callback_query.from_user.id)
        data = await state.get_data()
        messages_id = data['messages_id_list']
        if response['unsubscribed']:
            for message in messages_id:
                await bot.delete_message(chat_id=callback_query.from_user.id, message_id=message - 1)
            await bot.delete_messages(chat_id=callback_query.from_user.id, message_ids=messages_id)
            await bot.send_message(chat_id=callback_query.from_user.id, text=f'Вы отписались от мероприятия.',
                                   reply_markup=user_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id, text=f"Что-то пошло не так: {response['message']}",
                                   reply_markup=user_start_keyboard())
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.callback_query(F.data.contains('user_main_state'))
async def user_main_state(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await callback_query.message.edit_text(text='Это бот для канала Доски дяди Жени. '
                                                    'Здесь вы можете записаться на мероприятие.',
                                               reply_markup=user_start_keyboard())
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@user_router.message(F.text)
async def text_message_handler(message: Message, bot: Bot, state: FSMContext):
    try:
        user = message.from_user.id
        await bot.send_message(chat_id=message.from_user.id, text='Это бот для канала Доски дяди Жени. '
                                                                  'Здесь вы можете записаться на мероприятие.',
                               reply_markup=user_start_keyboard())
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))