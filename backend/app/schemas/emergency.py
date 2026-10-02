from pydantic import BaseModel, ConfigDict
from typing import Optional

class EmergencyNumberBase(BaseModel):
    label: str
    number: str
    category: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = "IN"

class EmergencyNumberResponse(EmergencyNumberBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    state: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)
