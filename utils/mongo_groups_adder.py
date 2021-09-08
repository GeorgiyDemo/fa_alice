"""
Скрипт для занесения данных о группах Финашки с fa.ru в MongoDB
Заносит все в нижнем регистре для совпадения по токенам
"""

import pymongo
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
CONNECTION_STR = os.getenv("CONNECTION_STR", None)
if CONNECTION_STR is None:
    raise ValueError("Не задана переменная окружения CONNECTION_STR!")

# Получаем данные
response = requests.get("https://schedule.fa.ru/api/groups.json").json()
for item in response:
    item["label_original"] = item["label"]
    item["label"] = item["label"].lower()
    print(f"{item['label_original']} {item['label']}")

# Подключаемся к БД
myclient = pymongo.MongoClient(CONNECTION_STR)
connection = myclient["fa_alice"]
group_table = connection["groups"]

# Заносим данные
group_table.insert_many(response)
print("Ok")