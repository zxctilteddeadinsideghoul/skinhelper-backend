from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "nF8da6ku7zih!"
    DB_PORT: str = "5464"
    DB_NAME: str = "skinhelper"
    DB_HOST: str = "localhost"

    ECHO: bool = False

    class Config:
        env_file = ".env"


config = Config()
