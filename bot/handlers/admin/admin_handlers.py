from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *
import itertools

admins_router = Router()


# Кнопка 'Записаться на мероприятие'
@admins_router.callback_query(F.data.contains('admin_subscribe_for_the_event'))
async def subscribe_for_the_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        event_list = repo.get_events()
        admin_id = str(callback_query.from_user.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text='Список мероприятий: ')
        for event in event_list:
            if repo.is_subscribed(event.id, admin_id):
                await bot.send_message(chat_id=callback_query.from_user.id,
                                       text=f"<u><b>{event.title}</b></u>\n\n"
                                            f"{event.description}\n\n"
                                            f"{event.date}",
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=InlineKeyboardMarkup(
                                           inline_keyboard=[[InlineKeyboardButton(text='Вы уже записаны',
                                                                                  callback_data=f"already_subscribed")],
                                                            [InlineKeyboardButton(text='Редактировать мероприятие',
                                                                                  callback_data=f"edit_event:{event.id}")]
                                                            ],
                                           resize_keyboard=True,
                                           one_time_keyboard=True))
            else:
                await bot.send_message(chat_id=callback_query.from_user.id,
                                       text=f"{event.title}\n\n"
                                            f"{event.description}\n\n"
                                            f"{event.date}",
                                       reply_markup=InlineKeyboardMarkup(
                                           inline_keyboard=[[InlineKeyboardButton(text='Записаться сюда',
                                                                                  callback_data=f"event_id:{event.id}")],
                                                            [InlineKeyboardButton(text='Редактировать мероприятие',
                                                                                  callback_data=f"edit_event:{event.id}")]
                                                            ],
                                           resize_keyboard=True,
                                           one_time_keyboard=True))
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


#-------------------------------------РЕДАКТИРОВАНИЕ МЕРОПРИЯТИЯ-----------------------------------------------
# @admins_router.callback_query(F.data.contains("edit_event"))
# async def edit_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     event_id_from_callback = int(callback_query.data.split(":")[1])
#     print(event_id_from_callback)
#     event_list = repo.get_events()
#     for event in event_list:
#         if event_id_from_callback == event.id:
#             await bot.send_message(chat_id=callback_query.from_user.id, text='Редактирование мероприятия:')
#             await bot.send_message(chat_id=callback_query.from_user.id,
#                                    text=f"{event.title}\n\n"
#                                         f"{event.description}\n\n"
#                                         f"{event.date}",
#                                    reply_markup=InlineKeyboardMarkup(
#                                        inline_keyboard=[[InlineKeyboardButton(text='Изменить заголовок',
#                                                                               callback_data=f"edit_title: {event.id}")],
#                                                         [InlineKeyboardButton(text='Изменить описание',
#                                                                               callback_data=f"edit_description: {event.id}")],
#                                                         [InlineKeyboardButton(text='Изменить дату',
#                                                                               callback_data=f"edit_date: {event.id}")]
#                                                         ],
#                                        resize_keyboard=True,
#                                        one_time_keyboard=True))
#         else:
#             await bot.send_message(chat_id=callback_query.from_user.id, text='Мероприятие не найдено.')
#
#
# @admins_router.callback_query(F.data.contains("edit_title"))
# async def edit_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     event_id_from_callback = int(callback_query.data.split(":")[1])
#     await state.set_state(states.set_new_event_title)
#     await state.set_data({'event_id': event_id_from_callback})
#     await bot.send_message(callback_query.from_user.id, text='Введите новое название мероприятия')
#
#
# @admins_router.message(states.set_new_event_title)
# async def new_event_title_set(message: Message, bot: Bot, state: FSMContext):
#     new_title = message.text
#     event_id = await state.get_data()
#     response = repo.edit_event(id=event_id, info={'title': new_title})
#
#     if response['changed']:
#         await bot.send_message(chat_id=message.from_user.id, text='Название мероприятия успешно изменено.',
#                                reply_markup=admins_start_keyboard())
#     else:
#         await bot.send_message(chat_id=message.from_user.id,
#                                text=f"Ошибка редактирования мероприятия: {response['message']}")


#-------------------------------------ПОКАЗАТЬ АДМИНОВ-----------------------------------------------
@admins_router.callback_query(F.data.contains('show_admins'))
async def show_admins(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        msg = await bot.send_message(chat_id=callback_query.from_user.id, text='Получение списка администраторов...')
        admins_list = repo.get_admins()
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=msg.message_id,
                                    text='Список администраторов: ')

        for admin in admins_list:
            sms = f"id: {admin.id}\n{admin.nickname}\n"
            await state.set_data({'sms': sms})
            await bot.send_message(chat_id=callback_query.from_user.id, text=sms,
                                   reply_markup=remove_admin_kb(admin.id))

        add_text = 'Чтобы добавить администратора, нажмите на кнопку ниже'
        await bot.send_message(chat_id=callback_query.from_user.id, text=add_text, reply_markup=add_admin_kb())

    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@admins_router.callback_query(F.data.contains('remove_admin'))
async def remove_admin(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        id = callback_query.data.split("_")[2]
        msg = await bot.send_message(chat_id=callback_query.from_user.id, text='Удаление администратора...')
        response = repo.remove_admin(id)
        if response['removed']:
            for i in range(1, len(repo.get_admins()) + 4):
                await bot.delete_message(chat_id=callback_query.from_user.id, message_id=msg.message_id - i)
            await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=msg.message_id,
                                        text='Администратор удален.', reply_markup=admins_start_keyboard())
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=f"Ошибка удаления администратора: {response['message']}")

    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@admins_router.callback_query(F.data.contains('add_admin'))
async def add_admin_id(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, text='Введите id пользователя')
    await state.set_state(states.set_id)


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

    if response['added']:
        await bot.send_message(chat_id=message.from_user.id, text='Администратор успешно добавлен!',
                               reply_markup=admins_start_keyboard())
        await state.clear()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Ошибка добавления администратора: {response['message']}")
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id,
                               text='Чтобы добавить администратора, нажмите на кнопку ниже',
                               reply_markup=add_admin_kb())


@admins_router.message(states.set_id)
async def add_admin_name(message: Message, bot: Bot, state: FSMContext):
    id = message.text
    # Проверка на корректность
    await state.set_state(states.set_name)
    await state.set_data({'id': id})
    await bot.send_message(chat_id=message.from_user.id, text='Введите имя пользователя')


# # ------------------------------------СПИСОК МЕРОПРИЯТИЙ-----------------------------------------------------
#
# @admins_router.callback_query(F.data.contains('all_events'))
# async def show_all_events(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     message_id = callback_query.message.message_id
#     await bot.edit_message_text(text='Получение всех мероприятий...', chat_id=callback_query.from_user.id,
#                                 message_id=message_id)
#     events = repo.get_events()
#     if len(events) == 0:
#         message = "Список ближайших мероприятий пуст"
#         await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
#                                     reply_markup=add_event_kb())
#     else:
#         message = "Список всех мероприятий: \n\n"
#         for e in events:
#             message += f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n\n"
#         await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
#                                     reply_markup=edit_events_kb())
#
# @admins_router.callback_query(F.data.contains('edit_list_events'))
# async def edit_event_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     message_id = callback_query.message.message_id
#     await bot.edit_message_text(text='Получение списка мероприятий...', chat_id=callback_query.from_user.id,
#                                 message_id=message_id)
#     events = repo.get_events()
#     await bot.edit_message_text(text='Список мероприятий:', chat_id=callback_query.from_user.id,
#                                 message_id=message_id)
#     for e in events:
#         message = f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n"
#         await bot.send_message(chat_id=callback_query.from_user.id, text=message, reply_markup=edit_or_delete_event_kb(e.id))
#
# # ------------------------------------ДОБАВИТЬ МЕРОПРИЯТИЕ-----------------------------------------------------
# @admins_router.callback_query(F.data.contains('add_event'))
# async def add_event_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
#     await state.set_state(states.set_event_title)
#     await bot.send_message(callback_query.from_user.id, text='Введите название мероприятия:')
#
#
# @admins_router.message(states.set_event_title)
# async def event_title_added(message: Message, bot: Bot, state: FSMContext):
#     event_title = message.text
#     await state.set_state(states.set_event_description)
#     await state.set_data({'title': event_title,
#                           'description': ''
#                           })
#     await bot.send_message(chat_id=message.from_user.id, text='Введите описание мероприятия')
#
#
# @admins_router.message(states.set_event_description)
# async def event_description_added(message: Message, bot: Bot, state: FSMContext):
#     event_description = message.text
#     await state.set_state(states.set_event_date)
#     await state.update_data({'description': event_description})
#     await bot.send_message(chat_id=message.from_user.id, text='Введите дату мероприятия в формате: 28/10/2024T10:00')
#
#
# @admins_router.message(states.set_event_date)
# async def event_date_added(message: Message, bot: Bot, state: FSMContext):
#     await bot.send_message(chat_id=message.from_user.id, text="Добавление мероприятия в таблицу...")
#     event_date = message.text
#     data = await state.get_data()
#     title = data['title']
#     description = data['description']
#     response = repo.add_event(EventModel(title=title, description=description, date=event_date))
#
#     if response['added']:
#         _message = "Мероприятие успешно добавлено!"
#         if "link" in response:
#             _message += f"\nСсылка на регистрацию: {response['link']}"
#         await bot.edit_message_text(text=_message, chat_id=message.from_user.id,
#                                     message_id=message.message_id + 1, reply_markup=admins_start_keyboard())
#     else:
#         await bot.edit_message_text(text=f"Ошибка добавления мероприятия: {response['message']}", chat_id=message.from_user.id,
#                                     message_id=message.message_id + 1, reply_markup=admins_start_keyboard())

@admins_router.message(F.text, StateFilter(None))
async def text_message_handler(message: Message, bot: Bot, state: FSMContext):
    try:
        user = message.from_user.id
        await bot.send_message(chat_id=message.from_user.id, text='Это бот для канала Доски дяди Жени. '
                                                                  'Здесь вы можете записаться на мероприятие.',
                               reply_markup=admins_start_keyboard())
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))
