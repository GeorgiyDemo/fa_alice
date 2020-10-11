import requests
import pymongo

connection_str = ""
mongo_client = pymongo.MongoClient(connection_str)
mongo_connection = mongo_client["fa_alice"]
table = mongo_connection["groups"]

groups_list = requests.get("https://schedule.fa.ru/api/groups.json").json()
for group in groups_list:
    group_label = group["label"]
    group["label"] = group_label.lower()
    group["label_original"] = group_label
    table.insert_one(group)
    print("Занесли группу {}".format(group_label))
