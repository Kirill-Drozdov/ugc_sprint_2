from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection


def insert_document(*, collection: Collection, data: dict) -> Any:
    res = collection.insert_one(data)
    result_id = res.inserted_id
    return result_id


def find(*, collection: Collection, condition: dict, multiple: bool = False):
    if multiple:
        results = collection.find(condition)
        return [item for item in results]
    return collection.find_one(condition)


def update_document(*, collection: Collection, condition: dict, new_values: dict):  # noqa
    collection.update_one(condition, {'$set': new_values})


def delete_document(*, collection: Collection, condition: dict):
    collection.delete_one(condition)


if __name__ == '__main__':
    # Создание клиента
    client = MongoClient('localhost', 27019)

    # Подключение к базе данных
    db = client['ugc']
