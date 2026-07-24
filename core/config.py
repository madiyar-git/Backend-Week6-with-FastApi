from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	DEBUG: bool = False
	
	SECRET_KEY: str
	
	ALLOWED_HOSTS: List[str] = ["127.0.0.1", "localhost"]
	
	# CORS
	CORS_ORIGINS: List[str] = []
	
	model_config = SettingsConfigDict(
		env_file=".env", env_file_encoding="utf-8", extra="ignore"
		)


settings = Settings()
