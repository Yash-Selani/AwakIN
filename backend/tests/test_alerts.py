from pathlib import Path
import xml.etree.ElementTree as ET
from app.services.alert_poller import parse_datetime

def test_parse_datetime():
    dt = parse_datetime("2026-10-05T12:00:00+05:30")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 5

def test_cap_parsing():
    fixture_path = Path(__file__).parent / "fixtures" / "sample_cap.xml"
    with open(fixture_path, "r", encoding="utf-8") as f:
        xml_data = f.read()

    root = ET.fromstring(xml_data)
    alerts = list(root.iter('{urn:oasis:names:tc:emergency:cap:1.2}alert'))
    assert len(alerts) == 1
    
    alert_elem = alerts[0]
    identifier = alert_elem.findtext('{urn:oasis:names:tc:emergency:cap:1.2}identifier')
    assert identifier == "SACHET-12345"

    info = alert_elem.find('{urn:oasis:names:tc:emergency:cap:1.2}info')
    assert info is not None

    event = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}event')
    assert event == "Heavy Rain"

    severity = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}severity')
    assert severity == "Severe"

    instruction = info.findtext('{urn:oasis:names:tc:emergency:cap:1.2}instruction')
    assert instruction == "Stay indoors and avoid travel."

    area = info.find('{urn:oasis:names:tc:emergency:cap:1.2}area')
    circle = area.findtext('{urn:oasis:names:tc:emergency:cap:1.2}circle')
    assert circle == "19.0760,72.8777 50.0"

    # Testing our splitting logic
    parts = circle.split()
    assert len(parts) == 2
    coords = parts[0].split(',')
    assert float(coords[0]) == 19.0760
    assert float(coords[1]) == 72.8777
    assert float(parts[1]) == 50.0
