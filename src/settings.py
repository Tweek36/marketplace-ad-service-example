from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # PostgreSQL configuration
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_database_name: str

    # Kafka configuration
    jwt_algorithm: str = "HS256"
    kafka_bootstrap_servers: str | None = None
    kafka_brokers: str | None = None
    kafka_topic_ads: str | None = None
    kafka_topic_marketplace_ads: str | None = None

    auth_service_url: str = "http://localhost:8000"
    jwt_secret: str = "change-me"

    database_url: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Build database URL from individual PostgreSQL variables
        self.database_url = f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"

        # Use KAFKA_BROKERS if provided (fallback to KAFKA_BOOTSTRAP_SERVERS)
        if self.kafka_brokers:
            self.kafka_bootstrap_servers = self.kafka_brokers
        elif not self.kafka_bootstrap_servers:
            raise ValueError(
                "Either KAFKA_BROKERS or KAFKA_BOOTSTRAP_SERVERS must be provided"
            )

        # Use KAFKA_TOPIC_MARKETPLACE_ADS if provided (fallback to KAFKA_TOPIC_ADS)
        if self.kafka_topic_marketplace_ads:
            self.kafka_topic_ads = self.kafka_topic_marketplace_ads
        elif not self.kafka_topic_ads:
            raise ValueError(
                "Either KAFKA_TOPIC_MARKETPLACE_ADS or KAFKA_TOPIC_ADS must be provided"
            )
