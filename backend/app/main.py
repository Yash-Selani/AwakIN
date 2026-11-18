import os
from fastapi import FastAPI, Depends, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from app.api.endpoints import disasters, emergency_numbers, departments, auth, places, ai_router, alerts, news
from app.api.deps import get_current_user, get_db
from app.core.firebase import initialize_firebase
from app.services.alert_poller import poll_cap_feed
from app.services.news_poller import poll_news
from app.core.config import settings

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

IS_VERCEL = os.environ.get("VERCEL", "") == "1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    
    if not IS_VERCEL:
        # Only run APScheduler locally — Vercel uses Cron Jobs instead
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(poll_cap_feed, 'interval', minutes=10)
        scheduler.add_job(poll_news, 'interval', minutes=10)
        scheduler.start()
        
        # Run once at startup
        scheduler.add_job(poll_cap_feed)
        scheduler.add_job(poll_news)
        
        yield
        
        # Shutdown
        scheduler.shutdown()
    else:
        yield

app = FastAPI(title="AwakIN API", version="1.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(
    disasters.router, 
    prefix="/api/disasters", 
    tags=["Disasters"], 
    dependencies=[Depends(get_current_user)]
)
app.include_router(emergency_numbers.router, prefix="/api/emergency-numbers", tags=["Emergency Numbers"])
app.include_router(
    departments.router, 
    prefix="/api/departments", 
    tags=["Departments"], 
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    places.router,
    prefix="/api/places",
    tags=["Places"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    ai_router,
    prefix="/api/ai",
    tags=["AI"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    alerts.router,
    prefix="/api/alerts",
    tags=["Alerts"]
    # Dependencies left out intentionally to allow public access or dashboard access
)
app.include_router(
    news.router,
    prefix="/api/news",
    tags=["News"]
)

class HealthCheckResponse(BaseModel):
    status: str
    message: str

class CronJobResponse(BaseModel):
    status: str
    job: str

def _verify_cron_secret(authorization: str | None) -> None:
    cron_secret = os.environ.get("CRON_SECRET") or settings.CRON_SECRET
    if cron_secret and authorization != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.api_route("/api/cron/poll-alerts", methods=["GET", "POST"], response_model=CronJobResponse, tags=["Cron"])
async def cron_poll_alerts(authorization: str | None = Header(default=None)):
    """Triggered by Vercel Cron Jobs (GET) or manual trigger (POST) to poll CAP alerts."""
    _verify_cron_secret(authorization)
    await poll_cap_feed()
    return CronJobResponse(status="ok", job="poll_cap_feed")

@app.api_route("/api/cron/poll-news", methods=["GET", "POST"], response_model=CronJobResponse, tags=["Cron"])
async def cron_poll_news(authorization: str | None = Header(default=None)):
    """Triggered by Vercel Cron Jobs (GET) or manual trigger (POST) to poll disaster news."""
    _verify_cron_secret(authorization)
    await poll_news()
    return CronJobResponse(status="ok", job="poll_news")

@app.get("/api/health", response_model=HealthCheckResponse)
@limiter.limit("10/minute")
async def health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify backend status.
    """
    try:
        await db.execute(text("SELECT 1"))
        return HealthCheckResponse(status="ok", message="AwakIN Backend is running smoothly.")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(status="error", message="Database connection failed.")
