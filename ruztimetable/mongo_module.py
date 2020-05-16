from datetime import datetime, timedelta

import pymongo
import yaml
class MongoClass:
    """Родительский класс для установки соединения"""
    
    def __init__(self):

        #with open("./settings.yml", 'r') as stream:
        connection_str = ""
        myclient = pymongo.MongoClient(connection_str)
        self.connection = myclient['fa_alice']

class MongoUserClass(MongoClass):
    """Класс для работы с пользователями"""

    def __init__(self):
        super().__init__()
        self.users_table = self.connection["users"]

    def find_user(self, user_id):
        """Возвращает boolean результат поиска пользователя в БД"""
        r = self.users_table.find_one({"user_id" : user_id})
        if r is None:
            return True
        return False
    
    def get_usergroup(self, user_id):
        """Получаем группу по пользователю"""
        return self.users_table.find_one({"user_id" : user_id},{"_id" : 0})

    def set_usergroup(self, user_id, group_id, group_name):
        """Выставляем группу пользователя"""
        self.users_table.insert_one({"user_id" : user_id, "group_id": group_id, "group_name" : group_name})
    
    def update_usergroup(self, user_id, group_id, group_name):
        """Обновляем группу пользователя"""
        self.users_table.update_one({"user_id": user_id}, {"$set": {"group_id": group_id,"group_name" : group_name}})
