from fa_api import FaAPI
from mongo_module import MongoUserClass


class UserCommandsClass():
    """Класс обработки команд от пользователя"""
    def __init__(self, user_id):
        self.out_str = None
        self.out_buttons = None
        self.user_id = user_id
        self.connector = MongoUserClass()

        router_dict = {
            "расписание" : 
            "Расписание на сегодня"
            "расписание на завтра"
            "расписание на послезавтра"
            "Изменение группы",
            "Расписаине на ДАТА"
            "": Просто 

        }

    def get_date(self):
        """Генерация даты на завтра/послезавтра"""
        pass

    def get_timetable(self):
        """Получение расписания"""
        fa = FaAPI()
        mongo_result = self.connector.get_usergroup(self.user_id)
        group_name, group_id = mongo_result["group_name"], mongo_result["group_id"]
        #Получаем инфо о расписании группы 
        timetable = fa.timetable_group(group_id, date, date)

        if len(timetable) == 0:
            return "Сегодня пар нет, отдыхайте!"

        out_str = "Расписание группы {} на {}:\n".format(group_name, "date")
        for i in range(len(timetable)):
            out_str +="{}. {}\n".format(i+1,timetable[i]["discipline"])
        return out_str
    
