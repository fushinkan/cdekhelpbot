from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки основного приложения.
    """
    
    # Telegram settings
    SECRET_TOKEN: str
    ADMIN_ID: int
    INVOICE_CHAT_ID: int
    
    # Redis URL
    REDIS_URL: str 
    
    #FastAPI URL
    BASE_FASTAPI_URL: str
    
    # PostgreSQL settings
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    
    @property
    def get_db(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    
    class Config:
        env_file = ".env"
    
    
settings = Settings()