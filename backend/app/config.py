import os

from pydantic import BaseModel


class Settings(BaseModel):
  database_url: str = os.getenv(
      "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_stock_lab"
  )
  jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
  ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


settings = Settings()
