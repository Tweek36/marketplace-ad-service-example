from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # PostgreSQL configuration
    postgres_username: str = "fake"
    postgres_password: str = "fake"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_database_name: str = "fake"
    postgres_connection_string: str | None = None

    # Kafka configuration
    jwt_algorithm: str = "HS256"
    kafka_bootstrap_servers: str | None = None
    kafka_brokers: str | None = None
    kafka_topic_ads: str | None = None
    kafka_topic_marketplace_ads: str | None = None

    auth_service_url: str = "http://student-tweek36-marketplace-auth-service-web.student-tweek36-marketplace-auth-service.svc.cluster.local:8000"
    jwt_secret: str = "change-me"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"
