"""
Навык Яндекс.Алисы Расписание Финансового университета

"""

from flask import Flask, request
from mongo_module import MongoUserClass, MongoBufferClass
from user_module import UserCommandsClass
from util_module import UtilClass

app = Flask(__name__)
user_mongo = MongoUserClass()
buf_mongo = MongoBufferClass()

@app.route('/', methods=['POST'])
def main():
    """Управляющая логика обработки входящего запроса на Flask"""

    out_dict = {}
    req = request.json

    #Если пользователь авторизован с акком Яндекса
    if "user" in req['session']:
        user_id = req['session']['user']['user_id']
    
    #Если без акка Яндекса
    else:
        user_id = req['session']['application']['application_id']

    user_command = req["request"]["command"]

    #Помощь и объяснение того, что происходит
    if "Помощь" in user_command or "помощь" in user_command:
        string = "Для начала мне необходимо узнать твою группу. После этого ты можешь получить расписание на сегодня, завтра и послезавтра одноименными командами."
        out_dict = UtilClass.json_generator(string)
    
    elif "Что ты умеешь" in user_command or "что ты умеешь" in user_command:
        string = "Я могу подсказать тебе расписание Финуниверситета на сегодня, завтра и послезавтра. Для этого скажи 'сегодня', 'завтра' или 'послезавтра'"
        out_dict = UtilClass.json_generator(string)
    
    # Если новый пользователь и его нет в таблице, значит это самое начало
    elif req['session']['new'] and user_mongo.find_user(user_id):
        string = "Привет! Я могу рассказать о твоем расписании в Финуниверситете.\nДля начала скажи название своей группы."
        out_dict = UtilClass.json_generator(string)

    # Если новый пользователь сказал название группы
    elif user_mongo.find_user(user_id):


        agreement_words = ["ага", "Ага", "Ды", "Да", "да",
                           "ды", "верно", "Верно", "Правильно", "правильно"]
        disagreement_words = ["не", "Нет", "Не", "Нит","нет"
                              "неправильно", "неверно", "Неверно", "Неправильно"]

        # Если пользователь согласился с тем, что это его группа
        if user_command in agreement_words and buf_mongo.user_exist(user_id):
            user_data = buf_mongo.get_data(user_id)

            user_mongo.set_usergroup(
                user_id, user_data["group_id"], user_data["group_name"])
            message_str = "Хорошо, я запомнила твою группу. Скажи \"Сегодня\" или \"Расписание\" для получения расписания на сегодня.".format(
                user_data["group_name"])
            out_dict = UtilClass.json_generator(
                message_str, ["Сегодня", "Завтра", "Послезавтра", "Изменение группы"])
            
            buf_mongo.remove_data(user_id)

        # Если пользователь не согласился со своей группой

        elif user_command in disagreement_words and buf_mongo.user_exist(user_id):

            suggestions = buf_mongo.get_data(user_id)["suggestions"]
            suggestions = None if suggestions == [] else suggestions
            out_dict = UtilClass.json_generator("Хорошо, попробуй произнести название группы еще раз.", suggestions)
            buf_mongo.remove_data(user_id)

        # Пользователь всёж сказал именно название группы
        else:
            print(request.json)
            # Ищем группу
            search_flag, search_dict = UtilClass.search_group(user_command)
            if not search_flag:
                out_dict = UtilClass.json_generator(
                    "Я не смогла найти твою группу, извини.\nМожет попробуешь назвать ее заново?")
            else:
                string = "Твоя группа {} и относится к {}, правильно?".format(search_dict["group_name"],
                                                                               search_dict["description"])
                out_dict = UtilClass.json_generator(string, ["Да", "Нет"])
                buf_mongo.add_data(user_id, search_dict)

    else:

        # Если действующий пользователь, то даем ему одно из расписаний
        obj = UserCommandsClass(user_id, user_command)
        out_dict = UtilClass.json_generator(obj.out_str, obj.out_buttons, obj.end_session)

    return out_dict


if __name__ == '__main__':
    app.run(debug=False, port=80)