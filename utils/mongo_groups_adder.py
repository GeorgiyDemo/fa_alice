"""
Скрипт для занесения данных о группах Финашки с fa.ru в MongoDB
Заносит все в нижнем регистре для совпадения по токенам
"""

import pymongo
import requests

connection_str = ""

# Получаем данные
r = requests.get("https://schedule.fa.ru/api/groups.json").json()
for d in r: d["label_original"] = d["label"]
for d in r: d["label"] = d["label"].lower()

# Подключаемся к БД
myclient = pymongo.MongoClient(connection_str)
connection = myclient["fa_alice"]
group_table = connection["groups"]

# Заносим данные
group_table.insert_many(r)
