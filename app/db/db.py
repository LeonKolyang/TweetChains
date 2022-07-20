from pymongo import MongoClient
from pymongo.database import Database
from app.core import di

class ApiDataBase:
    client: MongoClient = None


db = ApiDataBase()


def get_database() -> Database:
    db_config = di.get_db_config()

    return db.client[db_config.db_database]