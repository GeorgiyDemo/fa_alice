from fa_api import FaAPI
from mongo_module import MongoUserClass
import datetime

class UserCommandsClass():
    """Класс обработки команд от пользователя"""
    def __init__(self, user_id, command):
        
        self.out_str = None
        self.out_buttons = None
        self.end_session = False
        self.user_id = user_id
        self.connector = MongoUserClass()

        #TODO изменение группы
        router_dict = {
            "": self.begining,
            "Расписание" : self.timetable_today,
            "Расписание на сегодня" : self.timetable_today,
            "Расписание на завтра" : self.timetable_tomorrow,
            "Расписание на послезавтра" : self.timetable_aftertomorrow,
        }

        if command in router_dict:
            router_dict[command]()


    def begining(self):
        """Метод для начала работы"""
        self.out_str = "Здравствуйте, что вы хотите узнать?"
        self.out_buttons = ["Расписание на сегодня", "Расписание на завтра", "Расписание на послезавтра", "Изменение группы"]

    def timetable_today(self):
        """Расписание на сегодня"""
        date = datetime.datetime.now()
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.end_session = True

    def timetable_tomorrow(self):
        """Расписание на завтра"""
        date = datetime.datetime.now()+datetime.timedelta(days=1)
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.end_session = True

    def timetable_aftertomorrow(self):
        """Расписание на послезавтра"""
        date = datetime.datetime.now()+datetime.timedelta(days=3)
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.end_session = True

    def get_timetable(self, date_fa, date_normal):
        """Механизм получения расписания"""
        fa = FaAPI()
        mongo_result = self.connector.get_usergroup(self.user_id)
        group_name, group_id = mongo_result["group_name"], mongo_result["group_id"]
        #Получаем инфо о расписании группы 
        timetable = fa.timetable_group(group_id, date_fa)

        if len(timetable) == 0:
            return "Сегодня пар нет, отдыхайте!"

        out_str = "Расписание {} на {}:\n".format(group_name, date_normal)
        for i in range(len(timetable)):
            out_str +="{}. {}\n".format(i+1,timetable[i]["discipline"])
        return out_str
    
