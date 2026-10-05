from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AwakIN API"
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = "awakin_user"
    POSTGRES_PASSWORD: str = "awakin_password"
    POSTGRES_DB: str = "awakin_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    @property
    def async_database_url(self) -> str:
        # Fallback to SQLite if Docker is not available
        return "sqlite+aiosqlite:///./awakin.db"
    
    # External APIs
    GEMINI_API_KEY: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIREBASE_PROJECT_ID: str = ""
    SACHET_FEED_URL: str = "TODO_CONFIRM_URL"
    GOOGLE_MAPS_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
