from injector import Injector

from app.core.config import Config, DBConfig, TwitterAuthConfig
from app.service.service import Service

injector = Injector()


def get_config() -> Config:
    return injector.get(Config)


async def get_service() -> Service:
    return injector.get(Service)


def get_db_config() -> DBConfig:
    return injector.get(DBConfig)


def get_twitter_auth_config() -> TwitterAuthConfig:
    return injector.get(TwitterAuthConfig)