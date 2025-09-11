from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "google-gla:gemini-2.5-flash-lite"
    llm_batch_size: int = 10
    llm_fields_to_include: List[str] = ["title", "abstract"]

    scheduler_timezone: str = "US/Eastern"
    scheduler_hour: int = 20
    scheduler_minute: int = 0

    server_port: int = 8000


settings = Settings()
