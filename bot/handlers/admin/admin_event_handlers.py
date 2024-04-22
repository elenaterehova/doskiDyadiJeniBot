from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *
import itertools

admin_events_router = Router()

@admin_events_router.callback_query(F.data.contains("edit_event"))
async def edit_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    print(event_id_from_callback)
    event_list = repo.get_events()
    for event in event_list:
        if event_id_from_callback == event.id:
            await bot.send_message(chat_id=callback_query.from_user.id, text='Редактирование мероприятия:')
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=f"{event.title}\n\n"
                                        f"{event.description}\n\n"
                                        f"{event.date}",
                                   reply_markup=InlineKeyboardMarkup(
                                       inline_keyboard=[[InlineKeyboardButton(text='Изменить заголовок',
                                                                              callback_data=f"edit_title: {event.id}")],
                                                        [InlineKeyboardButton(text='Изменить описание',
                                                                              callback_data=f"edit_description: {event.id}")],
                                                        [InlineKeyboardButton(text='Изменить дату',
                                                                              callback_data=f"edit_date: {event.id}")]
                                                        ],
                                       resize_keyboard=True,
                                       one_time_keyboard=True))
        else:
            await bot.send_message(chat_id=callback_query.from_user.id, text='Мероприятие не найдено.')


@admin_events_router.callback_query(F.data.contains("edit_title"))
async def edit_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    await state.set_state(states.set_new_event_title)
    await state.set_data({'event_id': event_id_from_callback})
    await bot.send_message(callback_query.from_user.id, text='Введите новое название мероприятия')


@admin_events_router.message(states.set_new_event_title)
async def new_event_title_set(message: Message, bot: Bot, state: FSMContext):
    new_title = message.text
    event_id = await state.get_data()
    response = repo.edit_event(id=event_id, info={'title': new_title})

    if response['changed']:
        await bot.send_message(chat_id=message.from_user.id, text='Название мероприятия успешно изменено.',
                               reply_markup=admins_start_keyboard())
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Ошибка редактирования мероприятия: {response['message']}")

# ------------------------------------СПИСОК МЕРОПРИЯТИЙ-----------------------------------------------------

@admin_events_router.callback_query(F.data.contains('all_events'))
async def show_all_events(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    message_id = callback_query.message.message_id
    await bot.edit_message_text(text='Получение всех мероприятий...', chat_id=callback_query.from_user.id,
                                message_id=message_id)
    events = repo.get_events()
    if len(events) == 0:
        message = "Список ближайших мероприятий пуст"
        await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                    reply_markup=add_event_kb())
    else:
        message = "Список всех мероприятий: \n\n"
        for e in events:
            message += f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n\n"
        await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                    reply_markup=edit_events_kb())

@admin_events_router.callback_query(F.data.contains('edit_list_events'))
async def edit_event_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    message_id = callback_query.message.message_id
    await bot.edit_message_text(text='Получение списка мероприятий...', chat_id=callback_query.from_user.id,
                                message_id=message_id)
    events = repo.get_events()
    await bot.edit_message_text(text='Список мероприятий:', chat_id=callback_query.from_user.id,
                                message_id=message_id)
    for e in events:
        message = f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\n"
        await bot.send_message(chat_id=callback_query.from_user.id, text=message, reply_markup=edit_or_delete_event_kb(e.id))

# ------------------------------------ДОБАВИТЬ МЕРОПРИЯТИЕ-----------------------------------------------------
@admin_events_router.callback_query(F.data.contains('add_event'))
async def add_event_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(states.set_event_title)
    await bot.send_message(callback_query.from_user.id, text='Введите название мероприятия:')


@admin_events_router.message(states.set_event_title)
async def event_title_added(message: Message, bot: Bot, state: FSMContext):
    event_title = message.text
    await state.set_state(states.set_event_description)
    await state.set_data({'title': event_title,
                          'description': ''
                          })
    await bot.send_message(chat_id=message.from_user.id, text='Введите описание мероприятия')


@admin_events_router.message(states.set_event_description)
async def event_description_added(message: Message, bot: Bot, state: FSMContext):
    event_description = message.text
    await state.set_state(states.set_event_date)
    await state.update_data({'description': event_description})
    await bot.send_message(chat_id=message.from_user.id, text='Введите дату мероприятия в формате: 28/10/2024T10:00')


@admin_events_router.message(states.set_event_date)
async def event_date_added(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Добавление мероприятия в таблицу...")
    event_date = message.text
    data = await state.get_data()
    title = data['title']
    description = data['description']
    response = repo.add_event(EventModel(title=title, description=description, date=event_date))

    if response['added']:
        _message = "Мероприятие успешно добавлено!"
        if "link" in response:
            _message += f"\nСсылка на регистрацию: {response['link']}"
        await bot.edit_message_text(text=_message, chat_id=message.from_user.id,
                                    message_id=message.message_id + 1, reply_markup=admins_start_keyboard())
    else:
        await bot.edit_message_text(text=f"Ошибка добавления мероприятия: {response['message']}", chat_id=message.from_user.id,
                                    message_id=message.message_id + 1, reply_markup=admins_start_keyboard())


# ------------------------------------УДАЛИТЬ МЕРОПРИЯТИЕ-----------------------------------------------------
@admin_events_router.callback_query(F.data.contains('delete_event'))
async def edit_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    await bot.send_message(chat_id=callback_query.from_user.id, text='Удаление мероприятия...')
    repo.remove_event(id=event_id_from_callback)
    await bot.send_message(chat_id=callback_query.from_user.id, text='Мероприятие удалено')