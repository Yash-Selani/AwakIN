from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    lat: float
    lng: float

class Place(BaseModel):
    id: str
    name: str
    address: str
    location: Location
    open_now: Optional[bool] = None
    distance_meters: Optional[int] = None
    phone_number: Optional[str] = None
    google_maps_url: Optional[str] = None
    type: str

class PlacesResponse(BaseModel):
    places: List[Place]
