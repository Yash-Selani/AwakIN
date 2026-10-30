import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.main import app
from app.api.deps import get_current_user
from app.models.user import User
from app.models.disaster import DisasterType, DisasterGuide

# Fake user for overriding dependency
test_user = User(id="test-id-123", firebase_uid="mock-uid", email="test@example.com")

async def mock_get_current_user():
    return test_user

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_ai_guide_endpoint_success(async_client, db_session):
    disaster = DisasterType(slug="earthquake", name="Earthquake", icon="earthquake")
    db_session.add(disaster)
    await db_session.commit()
    await db_session.refresh(disaster)

    guide = DisasterGuide(
        disaster_type_id=disaster.id,
        before_steps={"step1": "Drop"},
        during_steps={"step1": "Cover"},
        after_steps={"step1": "Hold on"},
        first_aid={"step1": "Bandage"}
    )
    db_session.add(guide)
    await db_session.commit()

    payload = {
        "disaster_slug": "earthquake",
        "situation_text": "I am in my house and everything is shaking.",
        "lat": 12.34,
        "lon": 56.78,
        "language": "en"
    }

    with patch("app.api.endpoints.ai.genai.Client") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.text = '{"immediate_actions": ["If life is in danger, call 112", "Take cover."], "precautions": ["Stay away from windows."], "first_aid": ["Do not move seriously injured persons."], "what_not_to_do": ["Do not use elevators."], "who_to_call": ["112", "108"]}'
        
        mock_generate_content = MagicMock()
        mock_generate_content.return_value = mock_response
        mock_instance.models.generate_content = mock_generate_content

        response = await async_client.post("/api/ai/guide", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "immediate_actions" in data
        assert "If life is in danger, call 112" in data["immediate_actions"]

@pytest.mark.asyncio
async def test_ai_guide_endpoint_fallback_timeout(async_client, db_session):
    disaster = DisasterType(slug="earthquake2", name="Earthquake 2", icon="earthquake")
    db_session.add(disaster)
    await db_session.commit()

    payload = {
        "disaster_slug": "earthquake2",
        "situation_text": "I am in my house and everything is shaking.",
        "language": "en"
    }

    with patch("app.api.endpoints.ai.asyncio.to_thread") as mock_to_thread:
        async def slow_mock(*args, **kwargs):
            await asyncio.sleep(2)
            
        mock_to_thread.side_effect = slow_mock

        with patch("app.api.endpoints.ai.asyncio.wait_for", side_effect=asyncio.TimeoutError):
            response = await async_client.post("/api/ai/guide", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert "immediate_actions" in data
            assert len(data["immediate_actions"]) > 0

@pytest.mark.asyncio
async def test_ai_guide_rate_limit(async_client, db_session):
    disaster = DisasterType(slug="earthquake3", name="Earthquake 3")
    db_session.add(disaster)
    await db_session.commit()

    payload = {
        "disaster_slug": "earthquake3",
        "situation_text": "Test",
        "language": "en"
    }
    
    with patch("app.api.endpoints.ai.genai.Client") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.text = '{"immediate_actions": ["Call 112"], "precautions": [], "first_aid": [], "what_not_to_do": [], "who_to_call": []}'
        mock_instance.models.generate_content.return_value = mock_response
        
        # We need a fresh user id for rate limit test
        app.dependency_overrides[get_current_user] = lambda: User(id="rate-limit-user")
        
        # Fire 6 requests to hit the limit (limit is 5)
        for i in range(5):
            res = await async_client.post("/api/ai/guide", json=payload)
            assert res.status_code == 200
            
        res = await async_client.post("/api/ai/guide", json=payload)
        assert res.status_code == 429
        assert "Rate limit exceeded" in res.json()["detail"]
        
        # Reset override
        app.dependency_overrides.pop(get_current_user, None)
