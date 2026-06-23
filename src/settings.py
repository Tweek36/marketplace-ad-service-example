from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # PostgreSQL configuration
    postgres_username: str | None = None
    postgres_password: str | None = None
    postgres_host: str | None = None
    postgres_port: str | None = None
    postgres_database_name: str | None = None
    postgres_connection_string: str | None = None

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

        # Use POSTGRES_CONNECTION_STRING if provided
        if self.postgres_connection_string:
            self.database_url = self.postgres_connection_string
        else:
            # Fallback to individual PostgreSQL variables
            if (
                self.postgres_username
                and self.postgres_password
                and self.postgres_host
                and self.postgres_port
                and self.postgres_database_name
            ):
                self.database_url = f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"
            else:
                raise ValueError(
                    "Either POSTGRES_CONNECTION_STRING or all PostgreSQL connection parameters must be provided"  # noqa: E501
                )

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
