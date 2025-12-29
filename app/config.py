from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Конфигурация приложения из переменных окружения"""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    SQLITE_DB_PATH: str
    NATS_HOST: str
    NATS_PORT: int
    NATS_SUBJECT: str

    @property
    def DATABASE_URL_AIOSQLITE(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
    
    @property
    def NATS_URL(self) -> str:
        return f"nats://{self.NATS_HOST}:{self.NATS_PORT}"


config = Config()  # type: ignore[call-arg]

