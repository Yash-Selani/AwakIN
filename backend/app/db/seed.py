import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.disaster import DisasterType, DisasterGuide
from app.models.emergency import EmergencyNumber, Department
from app.models.user import User
from app.models.alert import Alert, NewsItem

async def seed_data():
    from app.db.database import engine
    from app.db.base_class import Base
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Clear existing data
        await session.execute(DisasterGuide.__table__.delete())
        await session.execute(DisasterType.__table__.delete())
        await session.execute(EmergencyNumber.__table__.delete())
        await session.execute(Department.__table__.delete())
        
        print("Seeding Disaster Types...")
        disasters = [
            {"slug": "earthquake", "name": "Earthquake", "icon": "activity", "severity_note": "Drop, Cover, and Hold on."},
            {"slug": "flood", "name": "Flood", "icon": "droplet", "severity_note": "Move to higher ground immediately."},
            {"slug": "cyclone", "name": "Cyclone", "icon": "wind", "severity_note": "Stay indoors and away from windows."},
            {"slug": "fire", "name": "Fire", "icon": "flame", "severity_note": "Get out, stay out, and call for help."},
            {"slug": "landslide", "name": "Landslide", "icon": "mountain", "severity_note": "Move away from the path of the landslide."},
            {"slug": "heatwave", "name": "Heatwave", "icon": "sun", "severity_note": "Stay hydrated and avoid sun exposure."},
            {"slug": "tsunami", "name": "Tsunami", "icon": "waves", "severity_note": "Move inland to higher ground."},
            {"slug": "industrial-accident", "name": "Industrial/Chemical Accident", "icon": "alert-triangle", "severity_note": "Evacuate upwind of the source."},
            {"slug": "medical-emergency", "name": "Medical Emergency", "icon": "heart-pulse", "severity_note": "Call ambulance immediately."},
            {"slug": "road-accident", "name": "Road Accident", "icon": "car-crash", "severity_note": "Secure the area and call emergency services."}
        ]
        
        disaster_objs = {}
        for d in disasters:
            dt = DisasterType(**d)
            session.add(dt)
            disaster_objs[d["slug"]] = dt
            
        await session.commit()
        
        print("Seeding Disaster Guides...")
        for dt in disaster_objs.values():
            guide = DisasterGuide(
                disaster_type_id=dt.id,
                before_steps={"steps": ["Prepare an emergency kit.", "Know the evacuation routes."]},
                during_steps={"steps": ["Stay calm.", "Follow official instructions."]},
                after_steps={"steps": ["Check for injuries.", "Do not enter damaged buildings."]},
                first_aid={"steps": ["Apply pressure to bleeding.", "Perform CPR if necessary."]}
            )
            session.add(guide)
            
        print("Seeding Emergency Numbers...")
        numbers = [
            {"label": "National Emergency Number", "number": "112", "category": "General"},
            {"label": "Police", "number": "100", "category": "Police"},
            {"label": "Fire Brigade", "number": "101", "category": "Fire"},
            {"label": "Ambulance", "number": "102", "category": "Medical"},
            {"label": "Emergency Disaster Management", "number": "108", "category": "General"},
            {"label": "Relief Commissioner For Natural Calamities", "number": "1070", "category": "Disaster"},
            # TODO: Verify if 1078 is correct for disaster/helpline context
            {"label": "Helpline (TODO verify)", "number": "1078", "category": "Helpline"},
            {"label": "Women Helpline", "number": "181", "category": "Helpline"},
            {"label": "Child Helpline", "number": "1098", "category": "Helpline"},
            # TODO: Verify if 1091 is Women Helpline or Anti-Stalking
            {"label": "Women Helpline (TODO verify)", "number": "1091", "category": "Helpline"},
            {"label": "NDMA Control Room", "number": "011-26701728", "category": "Disaster"}
        ]
        for n in numbers:
            session.add(EmergencyNumber(**n))
            
        print("Seeding Departments...")
        departments = [
            {"name": "National Disaster Management Authority (NDMA)", "category": "National", "phone": "011-26701728"},
            {"name": "National Disaster Response Force (NDRF)", "category": "Response", "phone": "011-24363260"},
            {"name": "State Disaster Response Force (SDRF)", "category": "State"},
            {"name": "India Meteorological Department (IMD)", "category": "Weather"},
            {"name": "Fire Services", "category": "Emergency"},
            {"name": "Civil Defence", "category": "Emergency"},
            {"name": "Health Department", "category": "Medical"},
            {"name": "Indian Red Cross Society", "category": "NGO"},
            {"name": "Police", "category": "Law Enforcement"}
        ]
        for dept in departments:
            session.add(Department(**dept))
            
        await session.commit()
        print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
