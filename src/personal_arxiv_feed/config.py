import appdirs
import json
import logging
from pathlib import Path


class Settings:
    def __init__(self, data):
        self.llm_model: str = data.get("llm_model", "google-gla:gemini-2.5-flash-lite")
        self.llm_batch_size: int = data.get("llm_batch_size", 10)
        self.llm_fields_to_include: list[str] = data.get(
            "llm_fields_to_include", ["title", "abstract"]
        )
        self.scheduler_timezone: str = data.get("scheduler_timezone", "US/Eastern")
        self.scheduler_hour: int = data.get("scheduler_hour", 20)
        self.scheduler_minute: int = data.get("scheduler_minute", 30)
        self.server_port: int = data.get("server_port", 8000)
        self.papers_per_page: int = data.get("papers_per_page", 20)
        self.arxiv_max_results_per_category: int = data.get(
            "arxiv_max_results_per_category", 1
        )


def load_settings() -> Settings:
    logger = logging.getLogger(__name__)
    config_dir = Path(appdirs.user_config_dir("personal-arxiv-feed"))
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    default_settings = {
        "llm_model": "google-gla:gemini-2.5-flash-lite",
        "llm_batch_size": 10,
        "llm_fields_to_include": ["title", "abstract"],
        "scheduler_timezone": "US/Eastern",
        "scheduler_hour": 20,
        "scheduler_minute": 30,
        "server_port": 8000,
        "papers_per_page": 20,
        "arxiv_max_results_per_category": 50,
    }

    if not config_file.exists():
        logger.info(f"creating config file {config_file}")
        with open(config_file, "w") as f:
            json.dump(default_settings, f, indent=4)
        user_settings = default_settings
    else:
        logger.info(f"reading from config file {config_file}")
        with open(config_file, "r") as f:
            user_settings = json.load(f)
        # Ensure all keys are present
        for key, value in default_settings.items():
            if key not in user_settings:
                user_settings[key] = value
        with open(config_file, "w") as f:
            json.dump(user_settings, f, indent=4)

    return Settings(user_settings)


settings = load_settings()
