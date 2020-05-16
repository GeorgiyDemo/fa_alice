"""
Навык Яндекс.Алисы для Фенашки

Основная логика:
Если новый пользователь:
- Спрашиваем группу пользователя
- Если группа не найдена, то сообщается об этом
- Если группа найдена, то спрашиваем подтверждение у пользователя, Ответ да/нет. Если да - устанавливаем. Если нет - просим повторить название группы

Если старый пользователь:
- Расписание на сегодня/расписание - показывает расписание на сегодня
- Расписание на завтра
- Расписание на послезавтра
- Расписание на ДАТА 01.03.2020 ?
- Возможность сменить группу

"""

from flask import Flask, request
from flask_restful import Resource, Api
import json
from fa_api import FaAPI
from mongo_module import MongoUserClass

app = Flask(__name__)
api = Api(app)
mongo = MongoUserClass()


#TODO
def search_group(group_name):
    """Метод для поиска группы"""

    group_name = group_name.replace(" ","")
    
    fa = FaAPI()
    #Получаем информацию о группе
    groups = fa.search_group(group_name)

    if len(groups) != 1:
        return False, ""

    description = groups[0]["description"]
    if "|" in description:
        description, _ = description.split("|")
    return True, description


def get_timetable(user_id, date=None):

    fa = FaAPI()
    mongo_result = mongo.get_usergroup(user_id)
    group_name, group_id = mongo_result["group_name"], mongo_result["group_id"]
    #Получаем инфо о расписании группы 
    timetable = fa.timetable_group(group_id, date, date)

    if len(timetable) == 0:
        return "Сегодня пар нет, отдыхайте!"

    out_str = "Расписание группы {} на {}:\n".format(group_name, "date")
    for i in range(len(timetable)):
        out_str +="{}. {}\n".format(i+1,timetable[i]["discipline"])
    return out_str


class MainClass(Resource):

    def post(self):

        out_dict = {
        "response": {"end_session": False},
        "version": "1.0"
        }

        req = request.json
        user_id = req['session']['user_id']
        

        #Если новый пользователь и его нет в таблице
        if req['session']['new'] and mongo.find_user(user_id):
            out_dict['response']['text'] = 'Привет, для начала назови свою группу'
        
        #Если новый пользователь сказал название группы
        elif mongo.find_user(user_id):
            
            user_command = req["request"]["command"]
            #Ищем группу
            search_flag, search_info = search_group(user_command)
            if not search_flag:
                out_dict['response']['text'] = 'Я не смогла найти вашу группу, извините.\nМожет попробуете назвать ее заново?'

            else:
                out_dict['response']['text'] = "Ваша группа относится к "+search_info+", верно ?"
                #Верно/Да
                #Ваша группа ДА/НЕТ?

                
                """
                хорошо, я запомнила вашу группу 
                - Расписание на сегодня/расписание - показывает расписание на сегодня
                - Расписание на завтра
                - Расписание на послезавтра
                - Расписание на ДАТА 01.03.2020 ?
                - Возможность сменить группу
                """


        else:
            #Если старый пользователь, то даем ему одно из расписаний
            """
                - Расписание на сегодня/расписание - показывает расписание на сегодня
                - Расписание на завтра
                - Расписание на послезавтра
                - Расписание на ДАТА 01.03.2020 ?
                - Возможность сменить группу
            """
            result_str = get_timetable()
            out_dict['response']['text'] = result_str
        
        return out_dict
           

api.add_resource(MainClass, '/')


if __name__ == '__main__':
    app.run(debug=False)
