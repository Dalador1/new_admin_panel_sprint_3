from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    es_host: str = "elasticsearch"
    es_port: int = 9200
    elastic_index: str = "movies"
    redis_host: str = "redis"
    redis_port: int = 6379
    poll_interval: int = 15

    @property
    def postgres_dsn(self) -> str:
        return (
            f"dbname={self.db_name} "
            f"user={self.db_user} "
            f"password={self.db_password} "
            f"host={self.db_host} "
            f"port={self.db_port}"
        )

    class Config:
        env_file = ".env"  # Убедитесь, что путь к файлу корректен