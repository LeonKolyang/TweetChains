from injector import inject, singleton

from app.core.config import Config


class Service:
    @inject
    @singleton
    def __init__(self, config: Config):
        self.config = config
