from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AwakIN API"
    
    # PostgreSQL Configuration
    DATABASE_URL: str = ""
    POSTGRES_USER: str = "awakin_user"
    POSTGRES_PASSWORD: str = "awakin_password"
    POSTGRES_DB: str = "awakin_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Neon/Vercel provides postgres:// or postgresql:// — SQLAlchemy async needs postgresql+asyncpg://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Translate libpq query params (e.g. Neon's sslmode/channel_binding) for asyncpg compatibility
            parsed = urlparse(url)
            if parsed.query:
                params = dict(parse_qsl(parsed.query, keep_blank_values=True))
                if "sslmode" in params and "ssl" not in params:
                    params["ssl"] = params.pop("sslmode")
                else:
                    params.pop("sslmode", None)
                params.pop("channel_binding", None)
                url = urlunparse(parsed._replace(query=urlencode(params)))
            return url

        # Local dev fallback
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # External APIs
    GEMINI_API_KEY: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIREBASE_CREDENTIALS_JSON: str = ""  # Base64-encoded service account JSON for Vercel
    FIREBASE_PROJECT_ID: str = ""
    SACHET_FEED_URL: str = "TODO_CONFIRM_URL"
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    
    # Vercel Cron Job protection
    CRON_SECRET: str = ""
    
    CORS_ORIGINS: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
