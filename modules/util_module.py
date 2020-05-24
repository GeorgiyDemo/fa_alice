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

    @staticmethod
    def wordintokens_full(words_list, token_list):
        """Поиск списка слов в токенах, полное совпадение"""
        return set(words_list) == set(token_list)

    @staticmethod
    def wordintokens_any(words_list, token_list):
        """Поиск списка слов в токенах, совпадение хотя бы по одному слову"""
        detected_words = []
        results_list = []
        for word in words_list:
            if word in token_list:
                detected_words.append(word)
                results_list.append(True)
            else:
                results_list.append(False)
        return any(results_list), detected_words
