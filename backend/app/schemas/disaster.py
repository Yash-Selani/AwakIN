from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class DisasterGuideBase(BaseModel):
    before_steps: Optional[Dict[str, Any]] = None
    during_steps: Optional[Dict[str, Any]] = None
    after_steps: Optional[Dict[str, Any]] = None
    first_aid: Optional[Dict[str, Any]] = None

class DisasterGuideResponse(DisasterGuideBase):
    id: str
    disaster_type_id: str
    
    model_config = ConfigDict(from_attributes=True)


class DisasterTypeBase(BaseModel):
    slug: str
    name: str
    icon: Optional[str] = None
    severity_note: Optional[str] = None

class DisasterTypeResponse(DisasterTypeBase):
    id: str
    guides: List[DisasterGuideResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
