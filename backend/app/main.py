from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.api.endpoints import disasters, emergency_numbers, departments, auth, places, ai_router, alerts, news
from app.api.deps import get_current_user
from app.core.firebase import initialize_firebase
from app.services.alert_poller import poll_cap_feed
from app.services.news_poller import poll_news

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    
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

app = FastAPI(title="AwakIN API", version="1.0.0", lifespan=lifespan)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite dev server
    # Add production frontend URL here later
]

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

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify backend status.
    """
    return HealthCheckResponse(status="ok", message="AwakIN Backend is running smoothly.")
