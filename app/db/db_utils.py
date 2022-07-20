from pymongo import MongoClient

from app.db.db import db
from app.core import di

def connect_to_mongo():
    """Initiate connection to mongoDB
    """
    db_config = di.get_db_config()
    db.client = MongoClient(db_config.db_uri)


def close_mongo_connection():
    """Close connection to mongoDB
    """
    db.client.close()
