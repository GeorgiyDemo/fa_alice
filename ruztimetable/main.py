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
from flask_restful import Resource
import json
from mongo_module import MongoUserClass
from user_module import UserCommandsClass
from util_module import UtilClass

app = Flask(__name__)
mongo = MongoUserClass()
buf_userdict = {}


@app.route('/', methods=['POST'])
def main():
    """Управляющая логика обработки входящего запроса на Flask"""

    out_dict = {}
    req = request.json
    user_id = req['session']['user_id']

    # Если новый пользователь и его нет в таблице, значит это самое начало
    if req['session']['new'] and mongo.find_user(user_id):
        out_dict = UtilClass.json_generator(
            "Привет, для начала скажи название своей группы")

    # Если новый пользователь сказал название группы
    elif mongo.find_user(user_id):

        user_command = req["request"]["command"]

        agreement_words = ["ага", "Ага", "Ды", "Да", "да",
                           "ды", "верно", "Верно", "Правильно", "правильно"]
        disagreement_words = ["не", "Нет", "Не", "Нит",
                              "неправильно", "неверно", "Неверно", "Неправильно"]

        # Если пользователь согласился с тем, что это его группа
        if user_command in agreement_words and user_id in buf_userdict:
            user_data = buf_userdict[user_id]

            mongo.set_usergroup(
                user_id, user_data["group_id"], user_data["group_name"])
            message_str = "Хорошо, я запомнила твою группу. Скажи \"Сегодня\" или \"Расписание\" для получения расписания на сегодня.".format(
                user_data["group_name"])
            out_dict = UtilClass.json_generator(
                message_str, ["Сегодня", "Завтра", "Послезавтра", "Изменение группы"])
            del buf_userdict[user_id]

        # Если пользователь не согласился со своей группой

        elif user_command in disagreement_words and user_id in buf_userdict:
            out_dict = UtilClass.json_generator(
                "Хорошо, попробуй произнести название группы еще раз")
            del buf_userdict[user_id]

        # Пользователь всёж сказал именно название группы
        else:
            user_command = req["request"]["command"]
            # Ищем группу
            search_flag, search_dict = UtilClass.search_group(user_command)
            if not search_flag:
                out_dict = UtilClass.json_generator(
                    "Я не смогла найти твою группу, извини.\nМожет попробуешь назвать ее заново?")

            else:
                out_dict = UtilClass.json_generator(
                    "Твоя группа относится к "+search_dict["description"]+", правильно ?", ["Да", "Нет"])
                buf_userdict[user_id] = search_dict

    else:

        # Если действующий пользователь, то даем ему одно из расписаний
        user_command = req["request"]["command"]
        obj = UserCommandsClass(user_id, user_command)
        out_dict = UtilClass.json_generator(obj.out_str, obj.out_buttons, obj.end_session)

    return out_dict


if __name__ == '__main__':
    app.run(debug=False)
