from pydantic_settings import BaseSettings, SettingsConfigDict

# Pydantic Settings (https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/)
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug: bool = False
    secret_key: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432

    # Property for get URL connection string
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()