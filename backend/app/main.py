from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.endpoints import disasters, emergency_numbers, departments

app = FastAPI(title="AwakIN API", version="1.0.0")

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
app.include_router(disasters.router, prefix="/api/disasters", tags=["Disasters"])
app.include_router(emergency_numbers.router, prefix="/api/emergency-numbers", tags=["Emergency Numbers"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])

class HealthCheckResponse(BaseModel):
    status: str
    message: str

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify backend status.
    """
    return HealthCheckResponse(status="ok", message="AwakIN Backend is running smoothly.")
