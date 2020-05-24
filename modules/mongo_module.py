import os

import pymongo


class MongoClass:
    """Родительский класс для установки соединения"""

    def __init__(self):
        connection_str = os.environ.get('CONNECTION_STR')
        myclient = pymongo.MongoClient(connection_str)
        self.connection = myclient['fa_alice']


class MongoBufferClass(MongoClass):
    """Класс хранения временных данных пользователей"""

    def __init__(self):
        super().__init__()
        self.buf_table = self.connection["buffer"]

    def user_exist(self, user_id):
        """Проверяет на существование данных"""

        if self.buf_table.find_one({"user_id": user_id}) is None:
            return False
        return True

    def set_data(self, user_id, userdata_dict):
        """Добавление данных"""

        userdata_dict["user_id"] = user_id
        self.buf_table.insert_one(userdata_dict)

    def get_data(self, user_id):
        """Получение данных"""

        r = self.buf_table.find_one({"user_id": user_id}, {"_id": 0, "user_id": 0})
        return r

    def remove_data(self, user_id):
        """Удаление данных"""

        self.buf_table.delete_many({"user_id": user_id})


class MongoUserClass(MongoClass):
    """Класс для работы с таблицей пользователей"""

    def __init__(self):
        super().__init__()
        self.users_table = self.connection["users"]

    def find_user(self, user_id):
        """Возвращает boolean результат поиска пользователя в БД"""
        r = self.users_table.find_one({"user_id": user_id})
        if r is None:
            return True
        return False

    def get_usergroup(self, user_id):
        """Получаем группу по пользователю"""
        return self.users_table.find_one({"user_id": user_id}, {"_id": 0})

    def set_usergroup(self, user_id, group_id, group_name):
        """Выставляем группу пользователя"""
        self.users_table.insert_one({"user_id": user_id, "group_id": group_id, "group_name": group_name})

    def update_usergroup(self, user_id, group_id, group_name):
        """Обновляем группу пользователя"""
        self.users_table.update_one({"user_id": user_id}, {"$set": {"group_id": group_id, "group_name": group_name}})

    def remove_user(self, user_id):
        """Удаление пользователя из БД. Необходимо для изменения группы"""
        self.users_table.delete_one({"user_id": user_id})


class MongoGroupsClass(MongoClass):
    """Класс для работы с таблицей групп"""

    def __init__(self):
        super().__init__()
        self.groups_table = self.connection["groups"]

    def get_groups(self):
        """Получаем все группы из таблицы"""
        return list(self.groups_table.find({}, {"_id": 0}))
