import httpx
import os
import math
import time
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Tuple, Any
from app.schemas.places import PlacesResponse, Place, Location

router = APIRouter()

# Simple in-memory cache: { (lat_round, lon_round, type, radius): (timestamp, response) }
places_cache: Dict[Tuple[float, float, str, int], Tuple[float, PlacesResponse]] = {}
CACHE_TTL = 300  # 5 minutes

def round_coord(coord: float) -> float:
    # Round to 3 decimal places (approx 111m precision)
    return round(coord, 3)

@router.get("/nearby", response_model=PlacesResponse)
async def get_nearby_places(
    lat: float = Query(..., description="Latitude of the center point"),
    lon: float = Query(..., description="Longitude of the center point"),
    type: str = Query(..., description="Type of place to search for (e.g., hospital, police)"),
    radius: int = Query(..., description="Radius in meters (e.g., 1000, 3000, 5000, 10000)")
):
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Places API key is missing.")

    # Cache key
    cache_key = (round_coord(lat), round_coord(lon), type, radius)
    current_time = time.time()

    # Check cache
    if cache_key in places_cache:
        cached_time, cached_response = places_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            return cached_response
        else:
            del places_cache[cache_key]

    # Google Places API (New) Nearby Search URL
    url = "https://places.googleapis.com/v1/places:searchNearby"

    # Map our types to Google Place Types if necessary
    # https://developers.google.com/maps/documentation/places/web-service/supported_types
    # Common types: hospital, fire_station, police, pharmacy
    # Blood bank might not be a standard type, so we might need a text search if it fails,
    # but for now we'll pass the type directly if it matches, or use includedTypes.
    
    # Standard mapping
    type_mapping = {
        "hospital": ["hospital"],
        "fire_station": ["fire_station"],
        "police": ["police"],
        "pharmacy": ["pharmacy"],
        "blood_bank": ["hospital", "health"] # Blood banks are tricky in nearby search, we can use hospital/health or fallback
    }

    included_types = type_mapping.get(type.lower(), [type.lower()])
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.currentOpeningHours,places.nationalPhoneNumber,places.googleMapsUri,places.primaryType"
    }
    
    payload = {
        "includedTypes": included_types,
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lon
                },
                "radius": float(radius)
            }
        }
    }
    
    # Blood bank is a special keyword, but Nearby Search (New) doesn't support text query directly.
    # Text Search (New) supports text queries. If the user passes blood_bank, we should maybe use text search.
    # But the prompt said: "Backend: GET /api/places/nearby?lat&lon&type&radius using Google Places API (New) Nearby Search"
    # and "(blood bank = search keyword)". 
    # Ah, Nearby Search (New) doesn't have a 'keyword' parameter. It only has includedTypes. 
    # Let's adjust to Text Search (New) for blood bank? Wait, the prompt says "Nearby Search".
    # Google Places API (New) Nearby Search supports `includedPrimaryTypes`, `includedTypes`.
    # It does NOT support keyword. Text Search supports keyword.
    # I'll stick to NearbySearch and use `includedTypes`. If it's blood bank, I'll use Text Search.
    
    async with httpx.AsyncClient() as client:
        if type.lower() == "blood_bank":
            url = "https://places.googleapis.com/v1/places:searchText"
            payload = {
                "textQuery": "blood bank",
                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lon
                        },
                        "radius": float(radius)
                    }
                }
            }
            # For text search, radius acts as a bias.
            
        response = await client.post(url, headers=headers, json=payload, timeout=10.0)

        if response.status_code != 200:
            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Permission denied to use Google Places API.")
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="API Quota exceeded.")
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Google Places API error: {response.text}")

        data = response.json()
        places_data = data.get("places", [])

        if not places_data:
            # Raise 404 or return empty? Prompt says "Handle zero results... with visible messages."
            # We can return an empty list and frontend handles it, or return a specific message.
            # Returning empty list is standard, frontend can show "Zero results".
            return PlacesResponse(places=[])

        normalized_places = []
        for p in places_data:
            # Calculate distance using Haversine formula since API (New) Nearby Search doesn't return distance
            p_lat = p.get("location", {}).get("latitude", 0)
            p_lon = p.get("location", {}).get("longitude", 0)
            
            # Distance calc
            R = 6371e3 # metres
            phi1 = lat * math.pi/180
            phi2 = p_lat * math.pi/180
            delta_phi = (p_lat-lat) * math.pi/180
            delta_lambda = (p_lon-lon) * math.pi/180
            
            a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c

            # open now status
            opening_hours = p.get("currentOpeningHours", {})
            open_now = opening_hours.get("openNow")

            # fallback to primaryType
            p_type = p.get("primaryType", type)
            if type.lower() == "blood_bank":
                p_type = "blood_bank"

            place_obj = Place(
                id=p.get("id"),
                name=p.get("displayName", {}).get("text", "Unknown Place"),
                address=p.get("formattedAddress", "No address available"),
                location=Location(lat=p_lat, lng=p_lon),
                open_now=open_now,
                distance_meters=int(distance),
                phone_number=p.get("nationalPhoneNumber"),
                google_maps_url=p.get("googleMapsUri"),
                type=p_type
            )
            normalized_places.append(place_obj)

        response_obj = PlacesResponse(places=normalized_places)
        
        # Cache it
        places_cache[cache_key] = (current_time, response_obj)
        
        return response_obj
