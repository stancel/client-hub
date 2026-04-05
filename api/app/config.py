from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "mariadb"
    db_port: int = 3306
    db_name: str = "dev_schema"
    db_user: str = "clienthub"
    db_password: str = ""
    api_key: str = "dev-api-key"
    api_host: str = "0.0.0.0"
    api_port: int = 8800

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
