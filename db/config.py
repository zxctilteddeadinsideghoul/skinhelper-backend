from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "nF8da6ku7zih!"
    DB_PORT: str = "5464"
    DB_NAME: str = "skinhelper"

    ECHO: bool = False

    class Config:
        env_file = ".env"
        env_prefix = 'DB_'


config = Config()
