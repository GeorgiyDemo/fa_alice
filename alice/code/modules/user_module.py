import datetime

from fa_api import FaAPI

from .mongo_module import MongoUserClass
from .util_module import UtilClass


class UserTokensClass:
    """Класс обработки команд от пользователя"""

    def __init__(self, user_id, tokens_list, user_command, new_request):

        self.out_str = None
        self.out_buttons = None
        self.end_session = False

        self.user_id = user_id
        self.new_request = new_request
        self.connector = MongoUserClass()
        self.defaultbutton = ["Сегодня", "Завтра", "Послезавтра", "Изменение группы"]

        # Список команд + словарь ассоциаций с методами
        words_list = [
            "расписание",
            "сегодня",
            "завтра",
            "послезавтра",
            "завершить",
            "спасибо",
            "выход",
            "изменение",
            "замена",
        ]
        router_dict = {
            "": self.begining,
            "расписание": self.timetable_today,
            "сегодня": self.timetable_today,
            "завтра": self.timetable_tomorrow,
            "послезавтра": self.timetable_aftertomorrow,
            "завершить": self.exit,
            "спасибо": self.exit,
            "выход": self.exit,
            "выйти": self.exit,
            "изменение": self.changegroup,
            "замена": self.changegroup,
        }

        result, detected_words = UtilClass.wordintokens_any(words_list, tokens_list)
        if result and len(detected_words) == 1:
            router_dict[detected_words[0]]()
        elif user_command == "":
            router_dict[user_command]()
        else:
            self.out_str = "Извини, я тебя не поняла.\nСкажи 'Помощь' и я помогу"
            self.out_buttons = self.defaultbutton

    def changegroup(self):
        """
        Логика изменения группы
        
        Удаляет пользователя с БД и он становится новым пользователем. Все гениальное - просто
        """
        self.connector.remove_user(self.user_id)
        self.out_str = "Хорошо, назови новую группу и я её запомню"

    def exit(self):
        """Логика завершения диалога"""
        self.out_str = "Обращайтесь"
        self.end_session = True

    def begining(self):
        """Метод для начала работы"""
        self.out_str = "Привет, на какой день ты хочешь узнать расписание?"
        self.out_buttons = self.defaultbutton

    def timetable_today(self):
        """Расписание на сегодня"""
        date = datetime.datetime.utcnow()
        date += datetime.timedelta(hours=3)
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.out_buttons = self.defaultbutton
        # Если это новая сессия, то значит команда была вызвана напрямую, а знчит надо выходить из навыка
        self.end_session = self.new_request

    def timetable_tomorrow(self):
        """Расписание на завтра"""
        date = datetime.datetime.utcnow() + datetime.timedelta(days=1, hours=3)
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.out_buttons = self.defaultbutton
        self.end_session = self.new_request

    def timetable_aftertomorrow(self):
        """Расписание на послезавтра"""
        date = datetime.datetime.utcnow() + datetime.timedelta(days=2, hours=3)
        l = [date.strftime("%Y.%m.%d"), date.strftime("%d.%m.%Y")]
        self.out_str = self.get_timetable(*l)
        self.out_buttons = self.defaultbutton
        self.end_session = self.new_request

    def get_timetable(self, date_fa, date_normal):
        """Механизм получения расписания"""
        fa = FaAPI()
        mongo_result = self.connector.get_usergroup(self.user_id)
        group_name, group_id = mongo_result["group_name"], mongo_result["group_id"]
        # Получаем инфо о расписании группы
        timetable = fa.timetable_group(group_id, date_fa, date_fa)

        if len(timetable) == 0:
            return "Пар нет, отдыхайте!"
        out_str = "Расписание {} на {}:\n".format(group_name, date_normal)

        for t in timetable:
            out_str += "{}. {} ({})\n".format(
                t["lessonNumberStart"], t["discipline"], t["kindOfWork"]
            )
        return out_str
