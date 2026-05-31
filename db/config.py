from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "nF8da6ku7zih!"
    DB_PORT: str = "5464"
    DB_NAME: str = "softcare"
    DB_HOST: str = "localhost"

    ECHO: bool = False
    API_TOKEN: SecretStr
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_IMAGE_CACHE_TOPIC: str = "product.image.cache.requests"
    KAFKA_IMAGE_CACHE_GROUP: str = "skinhelper-image-cache-worker"
    KAFKA_PRODUCER_MAX_BLOCK_MS: int = 1000
    KAFKA_PRODUCER_FLUSH_TIMEOUT: float = 1.0
    IMAGESERVICE_INTERNAL_URL: str = "http://imageservice:8080"
    IMAGES_PUBLIC_URL: str = "http://localhost"
    IMAGE_CACHE_REQUEST_TIMEOUT_SECONDS: float = 20.0

    class Config:
        env_file = ".env"


config = Config()
