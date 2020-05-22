import re
from .mongo_module import MongoGroupsClass

class SearchGroup:
    """Класс для поиска группы по токенам"""
    
    def __init__(self, token_list):

        self.token_list = token_list
        self.exists = False
        self.group_label = None
        self.group_id = None
        self.group_dict = {}
        
        #Получаем список групп
        mongo = MongoGroupsClass()
        groups_dict = mongo.get_groups()

        self.groups_list = [e["label"] for e in groups_dict]
        self.group_searcher()
        
        if self.exists:
            for e in groups_dict:
                if e["label"] == self.group_label:
                    self.group_id = str(e["id"])
                    self.group_label_original = e["label_original"]
                    self.group_dict = {"group_name": self.group_label_original, "group_id" : self.group_id}
            
    def groupbytoken(self, group):
        """
        Поиск по токенам
        
        - Возвращает кол-во символов вне шаблона
        - Возвращает boolean совпадения группы по шаблону 
        """

        results = []
        coords = []
        for token in self.token_list:
            
            #Если есть такой токен
            if token in group:
                
                #Флаг того, что мы что-то запомнили новое
                new_data = False
                #Индексы этого токена
                for match in re.finditer(token,group):

                    #Координаты для этого токена
                    locale_coords = range(match.start(),match.end())
                    
                    #Если их еще нет - добавляем в общие координаты
                    if not all([e in coords for e in locale_coords]):
                        results.append(True)
                        coords.extend(locale_coords)
                        new_data = True
                
                #Если уже зачли эти совпадения
                if not new_data:
                    results.append(False)

            #Если просто нет совпадения
            else:
                results.append(False)
        
        #Число символов, которые не вошли в шаблон
        #Чем больше это число, тем хуже
        diff = len(group)-len(coords)

        return all(results), diff

    def group_searcher(self):
        """
        Вызов поиска по токенам

        Получает все валидные результаты,
        далее отдает результат с наименьшим кол-вом символов, которые не вошли в шаблоны
        """
        
        result_list = []
        for group in self.groups_list:
            result = self.groupbytoken(group)
            #Если результат совпадения труъ - заносим в список результатов
            if result[0]:
                result_list.append((result[1],group))
        
        # Сортируем список по кол-ву символов вне шаблона
        result_list.sort(key=lambda x: x[0])

        #Выставляем первый элемент в результат, если такой есть
        if len(result_list) != 0:
            self.exists = True
            self.group_label = result_list[0][1]