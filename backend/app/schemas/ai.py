from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class AIGuideRequest(BaseModel):
    disaster_slug: str = Field(..., description="The slug of the disaster type")
    situation_text: str = Field(..., description="User's description of their situation")
    lat: Optional[float] = Field(None, description="Latitude")
    lon: Optional[float] = Field(None, description="Longitude")
    language: str = Field("en", description="Requested language code (en or hi)")

class AIGuideResponse(BaseModel):
    immediate_actions: List[str]
    precautions: List[str]
    first_aid: List[str]
    what_not_to_do: List[str]
    who_to_call: List[str]

class ExplainAlertRequest(BaseModel):
    alert_title: str
    alert_description: Optional[str] = None
    alert_instruction: Optional[str] = None
    alert_severity: Optional[str] = None

class ExplainAlertResponse(BaseModel):
    summary_en: str
    precautions_en: List[str]
    summary_hi: str
    precautions_hi: List[str]
