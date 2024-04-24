import itertools


class AdminModel:
    def __init__(self, id, nickname):
        self.id = id
        self.nickname = nickname

    @classmethod
    def mock(cls):
        return [AdminModel(123, 'NightBurgerus') for _ in range(0, 10)]

    @classmethod
    def parse(cls, object: list):
        return AdminModel(id=object[0], nickname=object[1])

class UserModel:
    def __init__(self, user_id, name, phone_number, telegram_link):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number
        self.telegram_link = telegram_link

    @classmethod
    def parse(cls, object: list):
        return UserModel(user_id=object[0], name=object[1], phone_number=object[2], telegram_link=object[3])
    @classmethod
    def mock(cls):
        return [UserModel(123, 'Терентьев Михал Палыч', '88005553535', 'NightBurgerus') for _ in range(0, 10)]

class EventModel:
    def __init__(self, id, title, description, date):
        self.id = id
        self.title = title
        self.description = description
        self.date = date

    @classmethod
    def parse(cls, object: list):
        return EventModel(id=object[0], title=object[1], description=object[2], date=object[3])
    @classmethod
    def mock(cls):
        return [EventModel('Event 123', 'Some description', '28/10/2024T10:00') for _ in range(0, 10)]
