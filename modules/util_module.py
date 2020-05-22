from fa_api import FaAPI


class UtilClass:

    @staticmethod
    def json_generator(text, buttons=None, end_session=False):
        """Генерация ответа в json"""

        out_dict = {
            "response": {},
            "version": "1.0",
        }
        out_dict['response']['end_session'] = end_session
        out_dict['response']['text'] = text

        if buttons is not None:
            out_dict['response']['buttons'] = [
                {"title": txt, "hide": True} for txt in buttons]

        return out_dict