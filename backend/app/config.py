from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SafeTrack"
    DEBUG: bool = True
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()