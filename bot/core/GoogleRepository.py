from bot.core.GoogleApi import GoogleSheetsAPI
from bot.core.Models import *
from typing import Final, Union

class GoogleRepository:
    def __init__(self, apiWorker: GoogleSheetsAPI):
        self.apiWorker = apiWorker
        self.admins_sheet_name: Final[str] = 'Администраторы'
        self.events_sheet_name: Final[str] = 'Мероприятия'

    # ---- ADMINS --------
    def get_admins(self) -> [AdminModel]:
        # Возвращает список администраторов
        objects = self.apiWorker.get(sheetName=self.admins_sheet_name, rows=-1, columns=2, start_row=2, start_column=1)
        res = []
        for i in range(0, len(objects)):
            if len(objects[i]) < 2:
                continue
            res.append(AdminModel.parse(object=objects[i]))
        return res


    def add_admin(self, admin: AdminModel) -> dict:
        # Добавляет администратора
        # При успешном добавлении возвращает объект:
        # {
        #   "added": True
        # }
        #
        # При неудачном добавлении:
        # {
        #   "added": False,
        #   "message": "<Сообщение ошибки>"
        # }

        # Проверка на наличие администратора
        admins = self.apiWorker.get(sheetName=self.admins_sheet_name, columns=1, start_row=2, start_column=1)
        if len(admins) > 0:
            for a in admins:
                if len(a) > 0 and a[0] == str(admin.id):
                    return {
                        "added": False,
                        "message": "Пользователь с таким id уже является администратором"
                    }

        # Добавление админа
        self.apiWorker.post(sheetName=self.admins_sheet_name, data=[[admin.id, admin.nickname]])
        admins = self.apiWorker.get(sheetName=self.admins_sheet_name, columns=1, start_row=2, start_column=1)
        if len(admins) == 0:
            return {
                "added": False,
                "message": "Ошибка добавления администратора"
            }

        print(admins)
        admins = list(filter(lambda x: x[0] == str(admin.id), admins))
        if len(admins) > 0:
            return { "added": True }

        return {
            "added": False,
            "message": "Ошибка добавления администратора"
        }

    def remove_admin(self, id: Union[int, str]) -> dict:
        # Удаляет администратора
        # При успешном удалении возвращает объект:
        # {
        #   "removed": True
        # }
        #
        # При неудачном удалении:
        # {
        #   "removed": False,
        #   "message": "<Сообщение ошибки>"
        # }
        admins = self.apiWorker.get(sheetName=self.admins_sheet_name, columns=1, start_row=2, start_column=1)
        if len(admins) == 0:
            return { "removed": False, "message": "Администратор не найден" }

        for i in range(1, len(admins) + 1):
            if len(admins[i - 1]) == 0:
                continue
            if str(admins[i - 1][0]) == str(id):
                res = self.apiWorker.clear_cells(sheetName=self.admins_sheet_name, rows=1, columns=2, start_column=1, start_row=i + 1)
                response = { "removed": res }
                if not res:
                    response["message"] = "Не удалось удалить администратора"
                return response
        return {"removed": False, "message": "Администратор не найден"}

    def is_admin(self, id: Union[int, str]):
        admins = self.get_admins()
        for admin in admins:
            if str(admin.id) == str(id):
                return True
        return False

    # ----- EVENTS -------
    def get_events(self) -> [EventModel]:
        # Возвращает список всех мероприятий
        # return EventModel.mock()

        events = self.apiWorker.get(sheetName=self.events_sheet_name, rows=-1, columns=4, start_row=2, start_column=1)
        res = []
        for i in range(0, len(events)):
            if len(events[i]) < 2:
                continue
            res.append(EventModel.parse(object=events[i]))
        return res

    def get_subscribed_users(self, event_id: Union[int, str]) -> [UserModel]:
        # Возвращает список пользователей, записавшихся на определённое мероприятие
        return UserModel.mock()

    def add_event(self, info: EventModel) -> dict:
        # Добавляет мероприятие
        # При успешном добавлении возвращает объект:
        # {
        #   "added": True,
        #   "link": t.me/...?register=id_<...>
        # }
        #
        # При неудачном добавлении:
        # {
        #   "added": False,
        #   "message": "<Сообщение ошибки>"
        # }
        # Проверка на наличие мероприятия

        # Получение всех мероприятий и поиск на такое же название
        events = self.apiWorker.get(sheetName=self.events_sheet_name, columns=3, start_row=2, start_column=2)
        if len(events) > 0:
            for event in events:
                if len(event) > 1 and str(event[0]).lower() == str(info.title).lower() and event[2] == info.date:
                    return {
                        "added": False,
                        "message": "мероприятие с таким названием и в это время уже существует."
                    }

        old_events_count = len(events)

        new_event_id = 1
        if len(events) > 0 and len(events[-1]) > 0 and len(str(events[-1][0])) > 0:
            new_event_id = int(events[-1][0]) + 1

        # Добавление мероприятия в лист "Мероприятия
        self.apiWorker.post(sheetName=self.events_sheet_name, data=[[new_event_id, info.title, info.description, info.date]])

        # Создание нового листа с именем мероприятия
        self.apiWorker.add_sheet(sheet_id=new_event_id, sheet_name=f"{info.title} {info.date}", header=['ID пользователя', 'ФИО', 'Телефон', 'Телеграм'])


        # Проверка на добавление мероприятия в общий список
        events = self.apiWorker.get(sheetName=self.events_sheet_name, columns=1, start_row=2, start_column=1)
        if len(events) == 0 or len(events) - old_events_count < 1:
            return {
                "added": False,
                "message": "Ошибка добавления мероприятия"
            }

        # self.apiWorker.post(sheetName=info.title, data=[['1', '2', '3', '4']])

        events = list(filter(lambda x: x[0] == str(new_event_id), events))
        if len(events) > 0:
            return {
                "added": True,
                "link": f"t.me/https://t.me/dyadyaJenaTest_bot?register=id_{new_event_id}"
            }

        return {
            "added": False,
            "message": "Ошибка добавления мероприятия"
        }

    def remove_event(self, id: Union[int, str]) -> dict:
        # Удаляет мероприятие
        # При успешном удалении возвращает объект:
        # {
        #   "removed": True
        # }
        #
        # При неудачном удалении:
        # {
        #   "removed": False,
        #   "message": "<Сообщение ошибки>"
        # }
        # TODO: не забыть удалить таблицу при удалении
        self.apiWorker.delete_sheet(sheet=id)
        return {"removed": True}

    def edit_event(self, id: Union[int, str], info: dict) -> dict:
        # Изменяет данные мероприятия
        # При успешном изменении возвращает объект:
        # {
        #   "changed": True
        # }
        #
        # При неудачном изменении:
        # {
        #   "changed": False,
        #   "message": "<Сообщение ошибки>"
        # }

        # Добавление админа
        # self.apiWorker.post(sheetName=self.admins_sheet_name, data=[[admin.id, admin.nickname]])
        # admins = self.apiWorker.get(sheetName=self.admins_sheet_name, columns=1, start_row=2, start_column=1)
        # if len(admins) == 0:
        #     return {
        #         "added": False,
        #         "message": "Ошибка добавления администратора"
        #     }
        #
        # print(admins)
        # admins = list(filter(lambda x: x[0] == str(admin.id), admins))
        # if len(admins) > 0:
        #     return {"added": True}
        #
        # return {
        #     "added": False,
        #     "message": "Ошибка добавления администратора"
        # }
        #
        return {"changed": True}

    # ------ USER INTERACTIVE ------
    def subscribe_to_the_event(self, event_id: Union[int, str], user: UserModel) -> dict:
        # Записывает пользователя на мероприятие
        # При успешной записи возвращает объект:
        # {
        #   "subscribed": True
        # }
        #
        # При неудачной записи:
        # {
        #   "subscribed": False,
        #   "message": "<Сообщение ошибки>"
        # }

        events = self.apiWorker.get(sheetName=self.events_sheet_name, columns=3)
        sheet_name = -1
        for e in events:
            print(e)
            if str(e[0]) == str(event_id):
                sheet_name = f"'{e[1]} {e[3]}'"

        data = [[user.user_id, user.name, user.phone_number, user.telegram_link]]
        res = self.apiWorker.post(sheetName=sheet_name, data=data)
        return {"subscribed": True}

    def unsubscribe_from_event(self, event_id: Union[int, str], user: UserModel) -> dict:
        # Удаляет пользователя из списка записанных на мероприятие
        # При успешном удалении возвращает объект:
        # {
        #   "unsubscribed": True
        # }
        #
        # При неудачном удалении:
        # {
        #   "unsubscribed": False,
        #   "message": "<Сообщение ошибки>"
        # }
        return {"unsubscribed": True}