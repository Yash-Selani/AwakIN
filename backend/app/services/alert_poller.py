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

_GEOCODE_CACHE: dict[tuple[float, float], tuple[str | None, str | None]] = {}

async def reverse_geocode(lat: float, lon: float) -> tuple[str, str]:
    """Returns (state, district) from Google Geocoding API."""
    if not settings.GOOGLE_MAPS_API_KEY:
        return None, None
        
    cache_key = (round(lat, 2), round(lon, 2))
    if cache_key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[cache_key]

    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={settings.GOOGLE_MAPS_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=3.0)
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
                    _GEOCODE_CACHE[cache_key] = (state, district)
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
            resp = await client.get(url, timeout=5.0)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch CAP feed, status: {resp.status_code}")
                return
            xml_data = resp.text
            
        root = ET.fromstring(xml_data)
        namespaces = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
        
        # Determine if it's RSS wrapping CAP or direct CAP
        # Simple approach: find all 'info' tags or 'alert' tags
        alerts_to_upsert = []
        
        # Support both namespaced and plain CAP alert elements
        cap_alerts = list(root.iter('{urn:oasis:names:tc:emergency:cap:1.2}alert')) or list(root.iter('alert'))
        
        for alert_elem in cap_alerts:
            identifier = alert_elem.findtext('{urn:oasis:names:tc:emergency:cap:1.2}identifier') or alert_elem.findtext('identifier')
            if not identifier:
                continue
                
            info = alert_elem.find('{urn:oasis:names:tc:emergency:cap:1.2}info')
            if info is None:
                info = alert_elem.find('info')
            if info is None:
                continue
                
            event = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}event') or info.findtext('event')
            severity = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}severity') or info.findtext('severity')
            urgency = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}urgency') or info.findtext('urgency')
            certainty = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}certainty') or info.findtext('certainty')
            headline = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}headline') or info.findtext('headline')
            description = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}description') or info.findtext('description')
            instruction = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}instruction') or info.findtext('instruction')
            effective_str = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}effective') or info.findtext('effective')
            expires_str = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}expires') or info.findtext('expires')
            
            effective = parse_datetime(effective_str) if effective_str else None
            expires = parse_datetime(expires_str) if expires_str else None
            
            area = info.find('{urn:oasis:names:tc:emergency:cap:1.2}area')
            if area is None:
                area = info.find('area')
            area_desc = None
            polygon = None
            circle = None
            lat, lon = None, None
            
            if area is not None:
                area_desc = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}areaDesc') or area.findtext('areaDesc')
                polygon = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}polygon') or area.findtext('polygon')
                circle = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}circle') or area.findtext('circle')
                
                # Derive lat, lon from circle (lat,lon radius)
                if circle:
                    parts = circle.split()
                    if len(parts) > 0:
                        coords = parts[0].split(',')
                        if len(coords) == 2:
                            try:
                                lat = float(coords[0])
                                lon = float(coords[1])
                            except ValueError:
                                pass
                            
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

        # If no direct CAP alert tags were found, parse RSS item tags
        if not alerts_to_upsert:
            for item in root.findall(".//item"):
                title = item.findtext("title")
                link = item.findtext("link")
                guid = item.findtext("guid")
                desc = item.findtext("description")
                category = item.findtext("category")
                pub_date_str = item.findtext("pubDate")
                identifier = guid or link or title
                if not identifier:
                    continue
                
                published_at = None
                if pub_date_str:
                    try:
                        from email.utils import parsedate_to_datetime
                        published_at = parsedate_to_datetime(pub_date_str)
                    except Exception:
                        pass
                
                alerts_to_upsert.append({
                    "source": "SACHET",
                    "external_id": identifier,
                    "title": title or "Alert",
                    "description": desc,
                    "severity": category or "Moderate",
                    "event": category or "Disaster Alert",
                    "urgency": "Expected",
                    "certainty": "Observed",
                    "instruction": desc,
                    "polygon": None,
                    "circle": None,
                    "area_desc": title,
                    "lat": None,
                    "lon": None,
                    "starts_at": published_at,
                    "expires_at": None,
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
