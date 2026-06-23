from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = ""
    postgres_username: str = ""
    postgres_password: str = ""
    postgres_host: str = ""
    postgres_port: str = "5432"
    postgres_database_name: str = ""

    jwt_algorithm: str = "HS256"
    kafka_bootstrap_servers: str = ""
    kafka_topic_ads: str = ""
    auth_service_url: str = ""
    jwt_secret: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (
            not self.database_url
            and self.postgres_username
            and self.postgres_password
            and self.postgres_host
            and self.postgres_database_name
        ):
            self.database_url = f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"

        if not self.kafka_bootstrap_servers:
            self.kafka_bootstrap_servers = "localhost:9092"
        if not self.kafka_topic_ads:
            self.kafka_topic_ads = "ads"
        if not self.auth_service_url:
            self.auth_service_url = "http://localhost:8000"
        if not self.jwt_secret:
            self.jwt_secret = "change-me"
