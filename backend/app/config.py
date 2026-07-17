from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    MODEL_API_URL: str
    MODEL_NAME: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings() -> Settings:
    config = Settings()
    print("DEBUG: Loaded fields:", config.model_fields_set)
    logger.info(f"Loaded fields: {config.MODEL_API_URL}, {config.MODEL_NAME}")
    return config