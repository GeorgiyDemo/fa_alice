"""
Навык Яндекс.Алисы "Расписание Финансового университета"
"""

from flask import Flask, request

from modules.mongo_module import MongoUserClass, MongoBufferClass
from modules.searchgroup_module import SearchGroup
from modules.user_module import UserTokensClass
from modules.util_module import UtilClass

app = Flask(__name__)
user_mongo = MongoUserClass()
buf_mongo = MongoBufferClass()


@app.route("/alice", methods=["POST"])
def main():
    """Управляющая логика обработки входящего запроса на Flask"""

    out_dict = {}
    req = request.json
    new_request = req["session"]["new"]

    # Если пользователь авторизован с акком Яндекса
    if "user" in req["session"]:
        user_id = req["session"]["user"]["user_id"]

    # Если без акка Яндекса
    else:
        user_id = req["session"]["application"]["application_id"]

    user_tokens = req["request"]["nlu"]["tokens"]
    user_command = req["request"]["command"]

    # Помощь и объяснение того, что происходит
    if UtilClass.wordintokens_full(["помощь"], user_tokens):
        string = "Для начала мне необходимо узнать твою группу. После этого ты можешь получить расписание на сегодня, завтра и послезавтра одноименными командами."
        out_dict = UtilClass.json_generator(string)

    elif UtilClass.wordintokens_full(["что", "ты", "умеешь"], user_tokens):
        string = "Я могу подсказать тебе расписание Финуниверситета на сегодня, завтра и послезавтра. Для этого скажи 'сегодня', 'завтра' или 'послезавтра'"
        out_dict = UtilClass.json_generator(string)

    # Если новый пользователь и его нет в таблице, значит это самое начало
    elif new_request and user_mongo.find_user(user_id):
        string = "Привет! Я могу рассказать о твоем расписании в Финуниверситете.\nДля начала скажи название своей группы."
        out_dict = UtilClass.json_generator(string)

    # Если новый пользователь сказал название группы
    elif user_mongo.find_user(user_id):

        agreement_words = ["ага", "ды", "да", "верно", "правильно"]
        disagreement_words = ["не", "нит", "нет", "неправильно", "неверно"]

        # Если пользователь согласился с тем, что это его группа
        if UtilClass.wordintokens_any(agreement_words, user_tokens)[
            0
        ] and buf_mongo.user_exist(user_id):
            user_data = buf_mongo.get_data(user_id)
            buf_mongo.remove_data(user_id)
            user_mongo.set_usergroup(
                user_id, user_data["group_id"], user_data["group_name"]
            )
            message_str = 'Хорошо, я запомнила твою группу. Скажи "Сегодня" или "Расписание" для получения расписания на сегодня.'
            out_dict = UtilClass.json_generator(
                message_str, ["Сегодня", "Завтра", "Послезавтра", "Изменение группы"]
            )

        # Если пользователь не согласился со своей группой
        elif UtilClass.wordintokens_any(disagreement_words, user_tokens)[
            0
        ] and buf_mongo.user_exist(user_id):
            buf_mongo.remove_data(user_id)
            out_dict = UtilClass.json_generator(
                "Хорошо, попробуй произнести название группы еще раз."
            )

        # Пользователь всёж сказал именно название группы
        else:

            # Ищем группу
            search_obj = SearchGroup(user_tokens)
            # Если существует
            if search_obj.exists:
                string = "Твоя группа {}, правильно?".format(
                    search_obj.group_label_original
                )
                out_dict = UtilClass.json_generator(string, ["Да", "Нет"])
                buf_mongo.set_data(user_id, search_obj.group_dict)
            else:
                string = "Я не смогла найти твою группу, извини.\nМожет попробуешь назвать ее заново?"
                out_dict = UtilClass.json_generator(string)

    else:

        # Если действующий пользователь, то даем ему одно из расписаний
        obj = UserTokensClass(user_id, user_tokens, user_command, new_request)
        out_dict = UtilClass.json_generator(
            obj.out_str, obj.out_buttons, obj.end_session
        )

    return out_dict


if __name__ == "__main__":
    app.run(debug=False, port=80)
