from pymongo import MongoClient
from pymongo.database import Database
from app.core import di

class ApiDataBase:
    client: MongoClient = None

db = ApiDataBase()


def get_database(test_instance=False) -> Database:
    db_config = di.get_db_config()

    if test_instance:
        return db.client[db_config.db_test_database]
    else:
        return db.client[db_config.db_database]