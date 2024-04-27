import re

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
        await bot.send_message(chat_id=callback_query.from_user.id, text='Список мероприятий: ')
        for event in event_list:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=f"{event.title}\n\n"
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


# Мероприятие выбрано, пользователь вводит свое имя
@user_router.callback_query(F.data.contains("event_id"))
async def event_chosen(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id = callback_query.data.split(':')[1]
    print(event_id)
    await state.set_data({'event_id': event_id, 'user_name': ''})
    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите ваше ФИО:")
    await state.set_state(states.set_user_name)


# Имя введено, пользователь вводит номер телефона
@user_router.message(states.set_user_name)
async def user_name_set(message: Message, bot: Bot, state: FSMContext):
    fio_pattern = re.compile(r'^(([А-Яа-яЁё]+)\\-?([А-Яа-яЁё]+))\\ (([А-Яа-яЁё]+)\\-?([А-Яа-яЁё]+))(\\ (([А-Яа-яЁё]+)\\-?([А-Яа-яЁё]+)))?$')
    user_name = message.text
    if fio_pattern.match(str(user_name)):
        await state.update_data({'user_name': user_name})
        await bot.send_message(chat_id=message.from_user.id, text="Введите свой номер телефона:")
        await state.set_state(states.set_user_phone_number)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="ФИО введено некорректно. Попробуйте снова.")
        await state.set_state(states.set_user_name)

# Номер телефона введен, данные сохраняются в таблицу
@user_router.message(states.set_user_phone_number)
async def user_phone_number_set(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

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
        await message.answer(text=f'Вы успешно записаны на мероприятие.', reply_markup=user_start_keyboard())
    else:
        await message.answer(text=f"Ошибка записи на мероприятие: {response['message']}",
                             reply_markup=user_start_keyboard())

    await state.clear()


@user_router.callback_query(F.data.contains('user_my_events'))
async def my_events_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    user = str(callback_query.from_user.id)
    events = repo.get_subscribed_events(user)
    message_id = callback_query.message.message_id
    await bot.edit_message_text(text='Получение всех мероприятий, на которые вы записаны...',
                                chat_id=callback_query.from_user.id,
                                message_id=message_id)
    if len(events) == 0:
        message = "Вы не записаны ни на одно мероприятие."
        await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                    reply_markup=user_start_keyboard())
    else:
        message = "Список мероприятий, на которые вы записаны: \n\n"
        for e in events:
            message += f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n\n"
        await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                    reply_markup=user_unsub_or_home_button())


@user_router.callback_query(F.data.contains('unsub_from_event'))
async def unsub_from_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.message.edit_text(text="Выберите мероприятие, от которого хотите отписаться")
    user = str(callback_query.from_user.id)
    events = repo.get_subscribed_events(user)
    messages_id_list = []
    for e in events:
        message = await bot.send_message(chat_id=callback_query.from_user.id,
                                         text=f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n\n",
                                         reply_markup=InlineKeyboardMarkup(
                                             inline_keyboard=[[InlineKeyboardButton(text='Отписаться',
                                                                                    callback_data=f"user_unsub_event:{e.id}")]],
                                             resize_keyboard=True,
                                             one_time_keyboard=True))
        messages_id_list.append(message.message_id)
    await state.set_data({'messages_id_list': messages_id_list})


@user_router.callback_query(F.data.contains('user_unsub_event'))
async def user_unsubscribe(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
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

@user_router.callback_query(F.data.contains('user_main_state'))
async def user_main_state(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.message.edit_text(text='Это бот для канала Доски дяди Жени. '
                                  'Здесь вы можете записаться на мероприятие.',
                             reply_markup=user_start_keyboard())
