from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *
from bot.keyboards.user.user_keyboard import *

user_router = Router()


@user_router.callback_query(F.data.contains('subscribe_for_the_event'))
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
                                                                              callback_data=f"event_id: {event.id}")]],
                                       resize_keyboard=True,
                                       one_time_keyboard=True))
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


# Мероприятие выбрано, пользователь вводит свое имя
@user_router.callback_query(F.data.contains("event_id"))
async def event_chosen(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id = callback_query.data
    await state.set_data({'event_id': event_id, 'user_name': ''})
    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите ваше имя:")
    await state.set_state(states.set_user_name)


# Имя введено, пользователь вводит номер телефона
@user_router.message(states.set_user_name)
async def user_name_set(message: Message, bot: Bot, state: FSMContext):
    user_name = message.text
    await state.update_data({'user_name': user_name})
    await bot.send_message(chat_id=message.from_user.id, text="Введите свой номер телефона:")
    await state.set_state(states.set_user_phone_number)


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
        await message.answer(text=f"Ошибка записи на мероприятие: {response['message']}", reply_markup=user_start_keyboard())

    shit = repo.get_subscribed_users(event_id=event)
    for i in shit:
        print(i.name)
    await state.clear()


# @user_router.callback_query(F.data.contains('my_events'))
# def my_events_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     user_events = repo.get_subscribed_users(event_id=)
