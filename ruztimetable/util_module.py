from fa_api import FaAPI


class UtilClass:

    @staticmethod
    def json_generator(text, buttons=None, end_session=False):
        """Генерация ответа в json"""

        out_dict = {
            "response":{},
            "version": "1.0",
        }
        out_dict['response']['end_session'] = end_session
        out_dict['response']['text'] = text
        
        if buttons is not None:
            out_dict['response']['buttons'] = [
                {"title": txt, "hide": True} for txt in buttons]

        return out_dict

    @staticmethod
    def search_group(group_name):
        """Поиск группы"""

        group_name = group_name.replace(" ", "")

        fa = FaAPI()
        # Получаем информацию о группе
        groups = fa.search_group(group_name)
        if len(groups) != 1:
            return False, {}

        description = groups[0]["description"]
        if "|" in description:
            description, _ = description.split("|")

        return True, {"description": description, "group_name": groups[0]["label"], "group_id": groups[0]["id"]}

