import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    db_host: str = os.getenv("DB_HOST", "db")
    db_name: str = os.getenv("DB_NAME", "fastapi_project_db")
    db_username: str = os.getenv("DB_USERNAME", "postgres_user")
    db_password: str = os.getenv("DB_PASSWORD", "postgres_pass")
    db_test_name: str = os.getenv("DB_TEST_NAME", "fastapi_project_test_db")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    max_connection_count: int = 10

    postgres_user: str = os.getenv("POSTGRES_USER", "postgres_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres_pass")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}"

    @property
    def database_test_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_test_name}"


settings = Settings()
