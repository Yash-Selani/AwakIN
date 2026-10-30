from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class AlertBase(BaseModel):
    source: str
    external_id: str
    title: str
    description: Optional[str] = None
    severity: Optional[str] = None
    
    event: Optional[str] = None
    urgency: Optional[str] = None
    certainty: Optional[str] = None
    instruction: Optional[str] = None
    polygon: Optional[str] = None
    circle: Optional[str] = None
    
    state: Optional[str] = None
    district: Optional[str] = None
    
    area_desc: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    raw: Optional[Any] = None

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: str
    fetched_at: datetime

    class Config:
        from_attributes = True
