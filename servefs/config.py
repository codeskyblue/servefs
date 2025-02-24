from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    BASIC_AUTH: str | None = None
    ROOT: Path = Path("./files")

    class Config:
        env_prefix = "SERVEFS_"

settings = Settings()