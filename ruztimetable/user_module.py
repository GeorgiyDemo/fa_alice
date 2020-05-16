from fa_api import FaAPI
import pymongo

def get_timetable(user_id, connector, date=None):

    fa = FaAPI()
    mongo_result = connector.get_usergroup(user_id)
    group_name, group_id = mongo_result["group_name"], mongo_result["group_id"]
    #Получаем инфо о расписании группы 
    timetable = fa.timetable_group(group_id, date, date)

    if len(timetable) == 0:
        return "Сегодня пар нет, отдыхайте!"

    out_str = "Расписание группы {} на {}:\n".format(group_name, "date")
    for i in range(len(timetable)):
        out_str +="{}. {}\n".format(i+1,timetable[i]["discipline"])
    return out_str

class UserCommandsClass():
    """Класс обработки команд от пользователя"""
    def __init__(self, user_id):
        self.out_str = None
        self.user_id = user_id
    
    
