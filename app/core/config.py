from pydantic import BaseSettings, Field, validator


class Config(BaseSettings):
    LOG_LEVEL: int = 20

    class Config:
        env_file = ".env"


class DBConfig(BaseSettings):
    db_username: str = Field(env="MONGO_DB_USER")
    db_password: str = Field(env="MONGO_DB_PASSWORD")
    db_database: str = Field(env="MONGO_DB_DATABASE")
    db_test_database: str = Field(env="MONGO_DB_TEST_DATABASE")
    db_uri: str = Field(None)

    class Config:
        env_file = ".env"
        
    @validator('db_uri', always=True)
    def ab(cls, v, values) -> str:
        return f"""mongodb+srv://{values["db_username"]}:{values["db_password"]}@cluster0.s4qfu.mongodb.net/"""\
            f"""{values["db_database"]}?retryWrites=true&w=majority"""


class TwitterAuthConfig(BaseSettings):
    consumer_key: str = Field("CONSUMER_KEY")
    consumer_secret: str = Field("CONSUMER_SECRET")

    class Config:
        env_file = ".env"