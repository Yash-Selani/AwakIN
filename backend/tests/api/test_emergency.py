import pytest
from app.models.emergency import EmergencyNumber, Department

@pytest.mark.asyncio
async def test_get_emergency_numbers(async_client, db_session):
    num = EmergencyNumber(label="Police", number="100", category="Police")
    db_session.add(num)
    await db_session.commit()
    
    response = await async_client.get("/api/emergency-numbers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["number"] == "100"

@pytest.mark.asyncio
async def test_get_departments(async_client, db_session):
    dept = Department(name="NDMA", category="National")
    db_session.add(dept)
    await db_session.commit()
    
    response = await async_client.get("/api/departments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "NDMA"
