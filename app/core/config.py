from pydantic import BaseSettings


class Config(BaseSettings):
    LOG_LEVEL: int = 20

    class Config:
        env_file = ".env"
