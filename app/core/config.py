from pydantic import BaseModel
import os

class Settings(BaseModel):
    APP_NAME: str = "Auth API"
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "6123"))

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "rinh_host")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5678"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "rinh_hack_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "rinh_hack_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "rinh_hack_pass")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "rinh-hack-2025")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "180"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
