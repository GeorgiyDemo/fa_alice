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

import yaml
import fa_api
from flask import Flask, request
from flask_restful import Resource, Api
import json
from fa_api import FaAPI


app = Flask(__name__)
api = Api(app)

def search_group(group_name):


def get_timetable(group_name):

    #Фикс группы из-за распознавания Алисы
    group_name = group_name.replace(" ","")
    out_str = ""
    fa = FaAPI()

    #Получаем информацию о группе
    groups = fa.search_group(group_name)

    if len(groups) == 0:
        return "Я не смогла найти вашу группу, простите"
    
    else:
        #Получаем инфо о расписании группы 
        timetable = fa.timetable_group(groups[0]["id"], "2020.05.13","2020.05.13")

        if len(timetable) == 0:
            return "Сегодня пар нет, отдыхайте!"

        for i in range(len(timetable)):
            out_str +="{}. {}\n".format(i+1,timetable[i]["discipline"])
        
        return out_str


class MainClass(Resource):

    def post(self):

        out_dict = {
        "response": {
            "text": "Привет",
            "end_session": False
        },
        "version": "1.0"
        }

        req = request.json

        #Если новый пользоватль
        if req['session']['new']:
            user_id = req['session']['user_id']
            out_dict['response']['text'] = 'Привет, для начала назови свою группу'

        
        #Если старый пользователь
        else:
            user_command = req["request"]["command"]
            result_str = get_timetable(user_command)
            out_dict['response']['text'] = result_str
        
        return out_dict
           

api.add_resource(MainClass, '/')


if __name__ == '__main__':
    app.run(debug=False)
