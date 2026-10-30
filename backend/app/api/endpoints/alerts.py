from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, cast, Float
from typing import List, Optional
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse
import math

router = APIRouter()

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in kilometers
    R = 6371.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    state: Optional[str] = None,
    district: Optional[str] = None,
    severity: Optional[str] = None,
    active: Optional[bool] = Query(False, description="Filter active alerts"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Alert)
    
    if state:
        query = query.where(Alert.state.ilike(f"%{state}%"))
    if district:
        query = query.where(Alert.district.ilike(f"%{district}%"))
    if severity:
        query = query.where(Alert.severity.ilike(severity))
        
    if active:
        now = datetime.now(timezone.utc)
        query = query.where(
            and_(
                or_(Alert.expires_at == None, Alert.expires_at > now),
                or_(Alert.starts_at == None, Alert.starts_at <= now)
            )
        )
    
    query = query.order_by(Alert.fetched_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/nearby", response_model=List[AlertResponse])
async def get_nearby_alerts(
    lat: float,
    lon: float,
    radius_km: float = Query(50.0, description="Radius in km for fallback center matching"),
    db: AsyncSession = Depends(get_db)
):
    # Fetch all active alerts first to filter in python (since we might have complex polygons, though we'll keep it simple here)
    now = datetime.now(timezone.utc)
    query = select(Alert).where(
        and_(
            or_(Alert.expires_at == None, Alert.expires_at > now),
            or_(Alert.starts_at == None, Alert.starts_at <= now)
        )
    )
    result = await db.execute(query)
    active_alerts = result.scalars().all()
    
    nearby = []
    for alert in active_alerts:
        # If the alert has lat/lon, use haversine to check if it's within radius
        if alert.lat is not None and alert.lon is not None:
            dist = haversine_distance(lat, lon, alert.lat, alert.lon)
            if dist <= radius_km:
                nearby.append(alert)
                continue
        # Check if circle exists (CAP format: "lat,lon radius")
        elif alert.circle:
            parts = alert.circle.split()
            if len(parts) >= 2:
                try:
                    alert_lat_lon = parts[0].split(',')
                    alert_lat = float(alert_lat_lon[0])
                    alert_lon = float(alert_lat_lon[1])
                    alert_rad = float(parts[1])
                    dist = haversine_distance(lat, lon, alert_lat, alert_lon)
                    if dist <= alert_rad:
                        nearby.append(alert)
                        continue
                except ValueError:
                    pass
        else:
            # If no coordinates, we could fallback to Geocoding the user's lat/lon to state/district and match those
            # But for simplicity, we return it if it has no specific polygon/circle to be safe (broad alert),
            # or skip it if we want strict nearby. We'll skip for now unless we implement reverse geocode here.
            # (In a real scenario, the backend poller already added state/district so we could match if we knew user's state)
            pass
            
    # Sort by severity conceptually (Extreme > Severe > Moderate > Minor)
    severity_order = {"Extreme": 0, "Severe": 1, "Moderate": 2, "Minor": 3}
    nearby.sort(key=lambda a: severity_order.get(a.severity, 99))
    
    return nearby
