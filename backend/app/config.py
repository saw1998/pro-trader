from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    '''Application settings loaded from environment variables'''

    # Application
    APP_NAME : str = "Pro Trader"
    APP_VERSION : str = "1.0.0"
    DEBUG : bool = True 
    ENVIRONMENT : str = "development"

    # Server
    HOST : str = "0.0.0.0"
    PORT : int = 8000
    WORKERS : int = 1

    #API
    API_V1_PREFIX : str = "api/v1"

    # PostgresSQL
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5432
    POSTGRES_USER : str = "postgres"
    POSTGRES_PASSWORD : str = ""
    POSTGRES_DB : str = "trading"

    # Connection pool settings
    DB_POOL_SIZE : int = 20
    DB_MAX_OVERFLOW : int = 10
    DB_POOL_RECYCLE : int = 300

    @property
    def DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://localhost:5432/pro_trader"
            # f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            # f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # REDIS
    REDIS_HOST : str = "localhost"
    REDIS_PORT : int = 6379
    REDIS_PASSWORD : str = ""
    REDIS_DB : int = 0
    REDIS_POOL_SIZE : int = 50

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Session
    SESSION_TTL_SECONDS : int = 1800 #30 min
    SESSION_REFRESH_THRESHOLD : int = 300 #refresh if less than 5 min left

    # Binance
    BINANCE_WS_URL : str = "wss://stream.binance.com:9443/ws"

    # Price buffering
    PRICE_BUFFER_INTERVAL_MS : int = 100 #100ms batching

    #Websocket
    WS_HEARTBEAT_INTERVAL: int = 30
    MAX_CONNECTIONS_PER_USER : int = 3

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS : int = 60

    # PnL calculation
    PNL_DEBOUNCE_MS : int = 50
    PNL_CACHE_TTL_SECONDS : int = 5

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    '''Cached settings instance'''
    return Settings()

settings = get_settings()

