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
from user_module import UserCommandsClass, get_timetable
app = Flask(__name__)
api = Api(app)
mongo = MongoUserClass()


#Штука для временного хранения данных о пользователе
buf_userdict = {}

class MainClass(Resource):

    def search_group(self, group_name):
        """Метод для поиска группы"""

        group_name = group_name.replace(" ","")
        
        fa = FaAPI()
        #Получаем информацию о группе
        groups = fa.search_group(group_name)

        if len(groups) != 1:
            return False, {}

        description = groups[0]["description"]
        if "|" in description:
            description, _ = description.split("|")
        
        return True, {"description" : description, "group_name" : groups[0]["label"], "group_id": groups[0]["id"]}


    def post(self):

        out_dict = {"response": {"end_session": False},"version": "1.0"}
        req = request.json
        user_id = req['session']['user_id']

        #Если новый пользователь и его нет в таблице, значит это самое начало
        if req['session']['new'] and mongo.find_user(user_id):
            out_dict['response']['text'] = 'Привет, для начала скажи название своей группы'
        
        #Если новый пользователь сказал название группы
        elif mongo.find_user(user_id):
            
            user_command = req["request"]["command"]

            agreement_words = ["ага","Ага","Ды", "Да", "да", "ды","верно","Верно","Правильно","правильно"]
            disagreement_words = ["не","Нет", "Не", "Нит","неправильно","неверно","Неверно","Неправильно"]
            
            #Если пользователь согласился с тем, что это его группа
            if user_command in agreement_words and user_id in buf_userdict:
                user_data = buf_userdict[user_id]

                mongo.set_usergroup(user_id, user_data["group_id"], user_data["group_name"])
                out_dict['response']['text'] = "Хорошо, я выставила группу {} для вас. Скажите \"расписание на сегодня\" для получения расписания.\nТакже могу подсказать расписание на завтра и любую другую дату".format(user_data["group_name"])

                del buf_userdict[user_id]

            #Если пользователь не согласился со своей группой

            elif user_command in disagreement_words and user_id in buf_userdict:
                out_dict['response']['text'] = "Хорошо, попробуйте произнести название группы еще раз"
                del buf_userdict[user_id]

            #Пользователь всёж сказал именно название группы
            else:
                user_command = req["request"]["command"]
                #Ищем группу
                search_flag, search_dict = self.search_group(user_command)
                if not search_flag:
                    out_dict['response']['text'] = 'Я не смогла найти вашу группу, извините.\nМожет попробуете назвать ее заново?'

                else:
                    out_dict['response']['text'] = "Ваша группа относится к "+search_dict["description"]+", правильно ?"
                    buf_userdict[user_id] = search_dict


        else:
           
            #Если действующий пользователь, то даем ему одно из расписаний
            
            """
                - Расписание на сегодня/расписание - показывает расписание на сегодня
                - Расписание на завтра
                - Расписание на послезавтра
                - Расписание на ДАТА 01.03.2020 ?
                - Возможность сменить группу
            """
            result_str = get_timetable(user_id, mongo)
            out_dict['response']['text'] = result_str
        
        return out_dict
           

api.add_resource(MainClass, '/')


if __name__ == '__main__':
    app.run(debug=False)
