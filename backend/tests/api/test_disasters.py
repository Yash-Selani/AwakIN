import pytest
from app.models.disaster import DisasterType

@pytest.mark.asyncio
async def test_get_disasters_empty(async_client):
    response = await async_client.get("/api/disasters/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_disasters_with_data(async_client, db_session):
    disaster = DisasterType(slug="test-disaster", name="Test Disaster")
    db_session.add(disaster)
    await db_session.commit()
    
    response = await async_client.get("/api/disasters/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "test-disaster"
    assert data[0]["name"] == "Test Disaster"
