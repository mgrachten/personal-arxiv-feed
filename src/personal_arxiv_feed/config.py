from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "google-gla:gemini-2.5-flash-lite"
    llm_batch_size: int = 10
    llm_fields_to_include: list[str] = ["title", "abstract"]

    # arXiv publishes submissions at 8pm US/Eastern time
    scheduler_timezone: str = "US/Eastern"
    scheduler_hour: int = 20
    scheduler_minute: int = 30

    server_port: int = 8000

    arxiv_max_results_per_category: int = 50


settings = Settings()
