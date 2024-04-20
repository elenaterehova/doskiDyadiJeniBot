from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *

admins_router = Router()

@admins_router.callback_query(F.data.contains('show_admins'))
async def show_admins(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    msg = await bot.send_message(chat_id=callback_query.from_user.id, text='Получение списка администраторов...')
    admins_list = repo.get_admins()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=msg.message_id,
                                text='Список администраторов: ')

    for admin in admins_list:
        sms = f"id: {admin.id}\n{admin.nickname}\n"
        await bot.send_message(chat_id=callback_query.from_user.id, text=sms, reply_markup=remove_admin_kb(admin.id))

    add_text = 'Чтобы добавить администратора, нажмите на кнопку ниже'
    await bot.send_message(chat_id=callback_query.from_user.id, text=add_text, reply_markup=add_admin_kb())


@admins_router.callback_query(F.data.contains('remove_admin'))
async def remove_admin(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    id = callback_query.data.split("_")[2]
    msg = await bot.send_message(chat_id=callback_query.from_user.id, text='Удаление администратора...')
    repo.remove_admin(id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id = msg.message_id-len(repo.get_admins()))
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=msg.message_id, text='Администратор удален.')
    # Удаляются все сообщения с именами админов
    #+ кнопки


@admins_router.callback_query(F.data.contains('add_admin'))
async def add_admin_id(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(states.set_id)
    await bot.send_message(callback_query.from_user.id, text='Введите id пользователя')


@admins_router.message(states.set_id)
async def add_admin_name(message: Message, bot: Bot, state: FSMContext):
    id = message.text
    # Проверка на корректность
    await state.set_state(states.set_name)
    await state.set_data({'id': id})
    await bot.send_message(chat_id=message.from_user.id, text='Введите имя пользователя')


@admins_router.message(states.set_name)
async def add_admin(message: Message, bot: Bot, state: FSMContext):
    id = await state.get_data()
    id = id['id']
    name = message.text
    response = repo.add_admin(AdminModel(id=id, nickname=name))
    # 3 главные кнопки
    #
    if response['added']:
        await bot.send_message(chat_id=message.from_user.id, text='Администратор успешно добавлены!')
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Ошибка добавления администратора: {response['message']}")
