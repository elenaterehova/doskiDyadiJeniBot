import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.handlers.general import states
from aiogram import Router, F, types, Bot
from bot.handlers.general import repo
from bot.keyboards.admin.admin_keyboard import *
from bot.core.Models import *
from bot.core.Constants import deeplink
import itertools

admin_events_router = Router()

async def remove_deleting_messages(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    key = f'deleting_messages_{callback_query.from_user.id}'
    if key in data:
        del data[key]
        await state.set_data(data=data)
async def remove_editing_message(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    key = f'edit_message_id_{callback_query.from_user.id}'
    if key in data:
        del data[key]
        await state.set_data(data=data)

async def remove_editing_mode_key(callback_query: types.CallbackQuery, state: FSMContext):
    key = f'is_editing_{callback_query.from_user.id}'
    user_id = callback_query.from_user.id
    data = await state.get_data()
    if key in data:
        del data[key]
        await state.set_data(data=data)

@admin_events_router.callback_query(F.data.contains("edit_event"))
async def edit_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        await remove_editing_message(callback_query, state)
        print(callback_query.data)
        event_id_from_callback = int(callback_query.data.split(":")[1])

        event_list = repo.get_events()
        for event in event_list:
            if str(event_id_from_callback) == str(event.id):
                # await bot.send_message(chat_id=callback_query.from_user.id, text='Редактирование мероприятия:')
                msg = await bot.send_message(chat_id=callback_query.from_user.id,
                                       text=f"Название: {event.title}\n\n"
                                            f"Описание:{event.description}\n\n"
                                            f"Дата: {event.date}",
                                       reply_markup=edit_event_kb(f'{event.id}'))
                state_data = await state.get_data()
                key = f'edit_message_id_{callback_query.from_user.id}'
                state_data[key] = msg.message_id
                await state.set_data(data=state_data)
                return
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Что-то пошло не так. Попробуйте снова.')
        print(str(e))


@admin_events_router.callback_query(F.data.contains("edit_title"))
async def edit_title(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    await state.set_state(states.set_new_event_title)
    await state.set_data({'event_id': event_id_from_callback, 'callback_query': callback_query})
    await bot.send_message(callback_query.from_user.id, text='Введите новое название мероприятия')


@admin_events_router.callback_query(F.data.contains("edit_description"))
async def edit_description(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    await state.set_state(states.edit_event_description)
    await state.set_data({'event_id': event_id_from_callback, 'callback_query': callback_query})
    await bot.send_message(callback_query.from_user.id, text='Введите новое описание мероприятия')


@admin_events_router.callback_query(F.data.contains("edit_date"))
async def edit_date(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = int(callback_query.data.split(":")[1])
    await state.set_state(states.edit_event_date)
    await state.set_data({'event_id': event_id_from_callback, 'callback_query': callback_query})
    await bot.send_message(callback_query.from_user.id, text='Введите новую дату мероприятия')

@admin_events_router.message(states.edit_event_description)
async def new_event_desctiption_set(message: Message,  bot: Bot, state: FSMContext):
    data = await state.get_data()
    data['is_description'] = True
    await state.set_data(data=data)
    await new_event_title_set(message, bot, state)

@admin_events_router.message(states.edit_event_date)
async def new_event_date_set(message: Message,  bot: Bot, state: FSMContext):
    data = await state.get_data()
    data['is_date'] = True
    await state.set_data(data=data)
    await new_event_title_set(message, bot, state)


@admin_events_router.message(states.set_new_event_title)
async def new_event_title_set(message: Message,  bot: Bot, state: FSMContext):
    new_title = message.text
    event_id = await state.get_data()

    print(event_id)
    _id = event_id['event_id']
    info = {}
    if 'is_description' in event_id:
        info = {
            'changing': 'description',
            'description': new_title
        }
    elif 'is_date' in event_id:
        info = {
            'changing': 'date',
            'date': new_title
        }
    else:
        info = {
            'changing': 'title',
            'new_title': new_title
        }

    response = repo.edit_event(id=_id, info=info)

    if response['changed']:
        await bot.send_message(chat_id=message.from_user.id, text='Данные мероприятия успешно изменены.')
        callback_query = event_id['callback_query']
        await edit_event(callback_query, bot, state)
        await state.clear()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Ошибка редактирования мероприятия: {response['message']}")
        await state.clear()

# ------------------------------------СПИСОК МЕРОПРИЯТИЙ-----------------------------------------------------

@admin_events_router.callback_query(F.data.contains('all_events'))
async def show_all_events(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    message_id = callback_query.message.message_id
    await bot.edit_message_text(text='Получение всех мероприятий...', chat_id=callback_query.from_user.id,
                                message_id=message_id)
    events = repo.get_events()

    state_data = await state.get_data()
    key = f'edit_message_id_{callback_query.from_user.id}'

    if len(events) == 0:
        message = "Список ближайших мероприятий пуст"
        await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                    reply_markup=add_event_kb())
    else:
        message = "Список всех мероприятий: \n\n"
        for e in events:
            message += f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\nСсылка на регистрацию: {deeplink}{e.id}\n\n"
            await bot.edit_message_text(text=message, chat_id=callback_query.from_user.id, message_id=message_id,
                                              reply_markup=edit_events_kb())
    state_data[key] = message_id
    await state.set_data(data=state_data)

@admin_events_router.callback_query(F.data.contains('edit_list_events'))
async def edit_event_list(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    message_id = callback_query.message.message_id
    await bot.edit_message_text(text='Получение списка мероприятий...', chat_id=callback_query.from_user.id,
                                message_id=message_id)
    await remove_editing_message(callback_query, state)
    events = repo.get_events()
    # await bot.delete_message(chat_id=callback_query.from_user.id, message_id=message_id)
    messages_id = []

    for i in range(0, len(events)):
        e = events[i]
        message = f"Название: {e.title}\nОписание: {e.description}\nДата: {e.date}\nСсылка: {deeplink}{e.id}"
        print(e.id)
        reply_markup = info_or_delete_event_kb(e.id)
        if i == len(events) - 1:
            reply_markup = info_or_delete_event_with_main_kb(e.id)

        if i > 0:
            msg = await bot.send_message(chat_id=callback_query.from_user.id, text=message,
                                         reply_markup=reply_markup)
        else:
            msg = await bot.edit_message_text(text=message,
                                              chat_id=callback_query.from_user.id,
                                              message_id=message_id,
                                              reply_markup=reply_markup)
        messages_id.append(msg.message_id)

    state_data = await state.get_data()
    if len(messages_id) == 1:
        key = f'edit_message_id_{callback_query.from_user.id}'
        state_data[key] = callback_query.message.message_id
        await remove_deleting_messages(callback_query, state)
    elif len(messages_id) > 1:
        state_data[f'deleting_messages_{callback_query.from_user.id}'] = messages_id
        await remove_editing_message(callback_query, state)
    await state.set_data(data=state_data)



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
    await bot.send_message(chat_id=message.from_user.id, text='Введите дату мероприятия в формате: 28.10.2024 10.00')


@admin_events_router.message(states.set_event_date)
async def event_date_added(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Добавление мероприятия в таблицу...")
    event_date = message.text
    data = await state.get_data()
    title = data['title']
    description = data['description']
    response = repo.add_event(EventModel(id=0, title=title, description=description, date=event_date))

    if response['added']:
        _message = "Мероприятие успешно добавлено!"
        if "link" in response:
            _message += f"\nСсылка на регистрацию: {response['link']}"
        await bot.edit_message_text(text=_message, chat_id=message.from_user.id,
                                    message_id=message.message_id + 1, reply_markup=admins_start_keyboard())
        await state.clear()
    else:
        await bot.edit_message_text(text=f"Ошибка добавления мероприятия: {response['message']}", chat_id=message.from_user.id,
                                    message_id=message.message_id + 1, reply_markup=admins_start_keyboard())
        await state.clear()


# ------------------------------------УДАЛИТЬ МЕРОПРИЯТИЕ-----------------------------------------------------
@admin_events_router.callback_query(F.data.contains('delete_event'))
async def delete_event(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = -1

    # Получение id удаляемого ивента из даты
    data = callback_query.data
    if len(data.split(":")) > 0:
        event_id_from_callback = data.split(":")[1]

    if event_id_from_callback == -1:
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Техническая проблема. Не удалось удалить мероприятие',
                               reply_markup=only_main_kb())
        return

    message = await bot.send_message(chat_id=callback_query.from_user.id, text='Удаление мероприятия...')
    await remove_editing_message(callback_query, state)
    res = repo.remove_event(id=event_id_from_callback)

    state_data = await state.get_data()

    if res['removed']:
        await bot.delete_message(chat_id=callback_query.from_user.id,
                                 message_id=message.message_id)
        events = res['events']

        # Если мероприятие удалялось из раздела инфо
        key = f'is_editing_{callback_query.from_user.id}'
        if key in state_data and state_data[key] is not None:
            await bot.edit_message_text(text='Мероприятие удалено',
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=only_main_kb())
            await remove_editing_mode_key(callback_query, state)
            key = f'edit_message_id_{callback_query.from_user.id}'
            state_data[key] = callback_query.message.message_id
            await state.set_data(data=state_data)
            return

        # Если удалено последнее мероприятие
        if len(events) == 2:
            await bot.edit_message_text(text='Список ближайших мероприятий пуст',
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=add_event_kb())
            key = f'edit_message_id_{callback_query.from_user.id}'
            state_data[key] = callback_query.message.message_id
            await state.set_data(data=state_data)

            return

        # Удаление сообщение с выбранным ивентом
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

        deleted_event_index = -1
        for i in range(0, len(events)):
            if len(events[i]) < 1:
                continue
            if str(events[i][0]) == str(event_id_from_callback):
                deleted_event_index = i
                break

        # Если удалённый ивент последний, то переносим кнопку "Главная" выше
        if deleted_event_index == len(events) - 1:
            event_id = events[-2][0]
            message_id = callback_query.message.message_id - 1
            reply_markup = info_or_delete_event_with_main_kb(id=event_id)
            chat_id = callback_query.from_user.id
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    else:
        error = ''
        if 'message' in res:
            error = res['message']
        await bot.edit_message_text(text=f"Ошибка удаления мероприятия: {error}",
                                    chat_id=callback_query.from_user.id,
                                    message_id=message.message_id,
                                    reply_markup=only_main_kb())


@admin_events_router.callback_query(F.data.contains('event_info'))
async def show_event_info(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    event_id_from_callback = -1

    msg = await bot.send_message(chat_id=callback_query.from_user.id,
                                 text='Получение данных мероприятия...')

    # Получение id удаляемого ивента из даты
    data = callback_query.data
    if len(data.split(":")) > 0:
        event_id_from_callback = data.split(":")[1]

    if event_id_from_callback == -1:

        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Техническая проблема. Не удалось удалить мероприятие',
                               reply_markup=only_main_kb())
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=msg.message_id)
        return

    event = repo.get_event_info(event_id=event_id_from_callback)
    if event == None:
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Техническая проблема. Не удалось удалить мероприятие',
                               reply_markup=only_main_kb())
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=msg.message_id)
        return


    text = f'Название: {event.title}\nОписание: {event.description}\nДата: {event.date}\n\nКто записался:\n'
    for user in event.users:
        text += f"{user.name} {user.phone_number}\n"

    if len(event.users) == 0:
        text += "–\n"


    state_data = await state.get_data()
    del_key = f'deleting_messages_{callback_query.from_user.id}'
    edit_key = f'edit_message_id_{callback_query.from_user.id}'
    del_ids = []
    edit_id = -1

    if del_key in state_data and state_data[del_key] is not None:
        del_ids = state_data[del_key]

    if edit_key in state_data and state_data[edit_key] is not None:
        edit_id = state_data[edit_key]
    else:
        edit_id = callback_query.message.message_id

    if len(del_ids) > 0 and edit_id != -1:
        del_ids = list(filter(lambda id: str(id) != str(edit_id), del_ids))


    if len(del_ids) > 0:
        for i in range(0, len(del_ids)):
            try:
                await bot.delete_message(chat_id=callback_query.from_user.id, message_id=del_ids[i])
            except:
                print("error here")
        await asyncio.sleep(1)

    edit_message_id = edit_id if edit_id != -1 else callback_query.message.message_id
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=msg.message_id)

    await bot.edit_message_text(text=text,
                                chat_id=callback_query.from_user.id,
                                message_id=edit_message_id,
                                reply_markup=event_info_kb(id=event_id_from_callback))

    await remove_deleting_messages(callback_query, state)
    state_data[edit_key] = edit_id
    is_editing_key = f'is_editing_{callback_query.from_user.id}'
    state_data[is_editing_key] = True
    await state.set_data(data=state_data)



