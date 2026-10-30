import logging
import httpx
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.alert import Alert
from app.core.config import settings
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def reverse_geocode(lat: float, lon: float) -> tuple[str, str]:
    """Returns (state, district) from Google Geocoding API."""
    if not settings.GOOGLE_MAPS_API_KEY:
        return None, None
        
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={settings.GOOGLE_MAPS_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    components = data["results"][0].get("address_components", [])
                    state = None
                    district = None
                    for comp in components:
                        if "administrative_area_level_1" in comp.get("types", []):
                            state = comp.get("long_name")
                        if "administrative_area_level_2" in comp.get("types", []):
                            district = comp.get("long_name")
                    return state, district
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
    return None, None

def parse_datetime(dt_str: str) -> datetime:
    try:
        # CAP dates are typically ISO 8601
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

async def poll_cap_feed():
    logger.info("Polling CAP feed...")
    url = settings.SACHET_FEED_URL
    if url == "TODO_CONFIRM_URL":
        logger.warning("SACHET_FEED_URL is not set. Skipping poll.")
        return
        
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch CAP feed, status: {resp.status_code}")
                return
            xml_data = resp.text
            
        root = ET.fromstring(xml_data)
        namespaces = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
        
        # Determine if it's RSS wrapping CAP or direct CAP
        # Simple approach: find all 'info' tags or 'alert' tags
        alerts_to_upsert = []
        
        # If it's an RSS feed, we might need to parse items, but let's assume we find CAP alerts
        for alert_elem in root.iter('{urn:oasis:names:tc:emergency:cap:1.2}alert'):
            identifier = alert_elem.findtext('{urn:oasis:names:tc:emergency:cap:1.2}identifier')
            if not identifier:
                continue
                
            info = alert_elem.find('{urn:oasis:names:tc:emergency:cap:1.2}info')
            if info is None:
                continue
                
            event = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}event')
            severity = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}severity')
            urgency = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}urgency')
            certainty = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}certainty')
            headline = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}headline')
            description = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}description')
            instruction = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}instruction')
            effective_str = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}effective')
            expires_str = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}expires')
            
            effective = parse_datetime(effective_str) if effective_str else None
            expires = parse_datetime(expires_str) if expires_str else None
            
            area = info.find('{urn:oasis:names:tc:emergency:cap:1.2}area')
            area_desc = None
            polygon = None
            circle = None
            lat, lon = None, None
            
            if area is not None:
                area_desc = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}areaDesc')
                polygon = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}polygon')
                circle = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}circle')
                
                # Derive lat, lon from circle (lat,lon radius)
                if circle:
                    parts = circle.split()
                    if len(parts) > 0:
                        coords = parts[0].split(',')
                        if len(coords) == 2:
                            lat = float(coords[0])
                            lon = float(coords[1])
                            
            state, district = None, None
            if lat is not None and lon is not None:
                state, district = await reverse_geocode(lat, lon)
                
            alerts_to_upsert.append({
                "source": "SACHET",
                "external_id": identifier,
                "title": headline or event or "Alert",
                "description": description,
                "severity": severity,
                "event": event,
                "urgency": urgency,
                "certainty": certainty,
                "instruction": instruction,
                "polygon": polygon,
                "circle": circle,
                "area_desc": area_desc,
                "lat": lat,
                "lon": lon,
                "starts_at": effective,
                "expires_at": expires,
            })
            
        async with AsyncSessionLocal() as db:
            # Delete expired
            now = datetime.now(timezone.utc)
            await db.execute(delete(Alert).where(Alert.expires_at < now))
            
            # Upsert
            for a in alerts_to_upsert:
                # Check if exists
                stmt = select(Alert).where(Alert.external_id == a["external_id"])
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    for k, v in a.items():
                        setattr(existing, k, v)
                else:
                    new_alert = Alert(**a)
                    db.add(new_alert)
                    
            await db.commit()
            logger.info(f"Processed {len(alerts_to_upsert)} CAP alerts.")
            
    except Exception as e:
        logger.error(f"Error polling CAP feed: {e}")
