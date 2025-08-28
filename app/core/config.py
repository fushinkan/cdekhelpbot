from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    """Класс с настройками для JWT"""
    
    private_key_path: Path = BASE_DIR / "security" / "private.pem"
    public_key_path: Path = BASE_DIR / "security" / "public.pem"
    algorithm: str = "RS256"
    
    
class Settings(BaseSettings):
    """
    Настройки основного приложения.
    """
    
    # JWT settings
    jwt_settings: AuthJWT = AuthJWT()
    
    # Telegram settings
    SECRET_TOKEN: str
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
    TEST_DB_NAME: str
    
    
    @property
    def get_db(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def get_test_db(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@localhost:5433/{self.TEST_DB_NAME}"
    

    model_config = SettingsConfigDict(env_file=".env")
    
    
settings = Settings()