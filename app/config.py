from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, EmailStr, AnyUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: EmailStr
    SMTP_PASSWORD: str
    EMAIL_FROM: EmailStr

    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost", "http://localhost:8080"]
    ADMIN_SECRET_KEY: str
    ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_ALLOWED_ORIGINS: list[str] = ["http://admin.localhost"]
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()