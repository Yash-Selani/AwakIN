import asyncio
import logging
import json
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Tuple

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AIGuideRequest, AIGuideResponse
from app.repositories.disaster import disaster_repo
from app.core.config import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory rate limiter
# Dictionary mapping user_id to a list of timestamps of their requests
RATE_LIMIT_STORE: Dict[str, list[float]] = {}
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW_SEC = 60

def check_rate_limit(user_id: str):
    now = time.time()
    user_requests = RATE_LIMIT_STORE.get(user_id, [])
    
    # Filter out old requests
    user_requests = [req_time for req_time in user_requests if now - req_time < RATE_LIMIT_WINDOW_SEC]
    
    if len(user_requests) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    
    user_requests.append(now)
    RATE_LIMIT_STORE[user_id] = user_requests


def generate_fallback_response(disaster, lang: str) -> AIGuideResponse:
    # Just format the DB guide directly
    guide = disaster.guides[0] if disaster.guides else None
    
    immediate = ["Seek safe shelter immediately.", "Stay tuned to local alerts."]
    if guide and guide.during_steps:
        # Flatten dictionary or grab values
        if isinstance(guide.during_steps, dict):
             immediate = list(guide.during_steps.values())[:3]
    
    precautions = ["Keep an emergency kit ready."]
    if guide and guide.before_steps:
        if isinstance(guide.before_steps, dict):
            precautions = list(guide.before_steps.values())[:3]
            
    first_aid = ["Only perform first aid if you are trained."]
    if guide and guide.first_aid:
        if isinstance(guide.first_aid, dict):
            first_aid = list(guide.first_aid.values())[:3]
            
    return AIGuideResponse(
        immediate_actions=immediate,
        precautions=precautions,
        first_aid=first_aid,
        what_not_to_do=["Do not panic.", "Do not spread rumors.", "Do not ignore official warnings."],
        who_to_call=["112 (National Emergency Number)", "108 (Ambulance)", "101 (Fire)"]
    )

@router.post("/guide", response_model=AIGuideResponse)
async def generate_ai_guide(
    request: AIGuideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI situation guide using Gemini based on the user's situation text,
    falling back to static guides if Gemini fails or times out.
    """
    check_rate_limit(str(current_user.id))
    
    disaster = await disaster_repo.get_by_slug_with_guides(db, slug=request.disaster_slug)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster type not found")
        
    guide_context = ""
    if disaster.guides:
        guide = disaster.guides[0]
        guide_context = f"""
        Official Guide Context for {disaster.name}:
        Before: {json.dumps(guide.before_steps)}
        During: {json.dumps(guide.during_steps)}
        After: {json.dumps(guide.after_steps)}
        First Aid: {json.dumps(guide.first_aid)}
        """

    system_prompt = f"""You are a calm, professional emergency response assistant for AwakIN.
Your response MUST always begin with: "If life is in danger, call 112"
Tone: calm, reassuring, urgent but not panicky.
Format: Short numbered steps in each section.
Location-specific context: Use India-specific emergency numbers (112, 108, 101, etc.). Do NOT invent local facts.
Medical Rule: NEVER give medical diagnosis or medication dosage.
Language: Respond entirely in {request.language}.

Use the following Official Guide Context as grounding information, but adapt it to the user's specific situation text.
If the prompt is unrelated to an emergency, disaster, or safety, firmly but politely refuse and advise the user to only use this for safety situations.

{guide_context}
"""

    user_prompt = f"Situation: {request.situation_text}"
    if request.lat is not None and request.lon is not None:
        user_prompt += f"\nLocation: Latitude {request.lat}, Longitude {request.lon}"

    try:
        # Wrap Gemini call in timeout
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        async def call_gemini():
            return await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "immediate_actions": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "precautions": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "first_aid": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "what_not_to_do": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "who_to_call": {"type": "ARRAY", "items": {"type": "STRING"}}
                        },
                        "required": ["immediate_actions", "precautions", "first_aid", "what_not_to_do", "who_to_call"]
                    },
                    temperature=0.2
                )
            )

        response = await asyncio.wait_for(call_gemini(), timeout=20.0)
        
        raw_json = response.text
        data = json.loads(raw_json)
        
        # Ensure the rule "If life is in danger, call 112" is at the top of immediate actions if not already added by the model.
        if "immediate_actions" in data:
            has_warning = any("call 112" in action.lower() for action in data["immediate_actions"])
            if not has_warning:
                data["immediate_actions"].insert(0, "If life is in danger, call 112")
                
        return AIGuideResponse(**data)
        
    except asyncio.TimeoutError:
        logger.warning(f"Gemini API timeout for disaster {request.disaster_slug}")
        return generate_fallback_response(disaster, request.language)
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        # Fallback to static guide
        return generate_fallback_response(disaster, request.language)

from app.schemas.ai import ExplainAlertRequest, ExplainAlertResponse

@router.post("/explain-alert", response_model=ExplainAlertResponse)
async def explain_alert(
    request: ExplainAlertRequest,
    current_user: User = Depends(get_current_user)
):
    check_rate_limit(str(current_user.id))
    
    system_prompt = """You are a calm, professional emergency response assistant for AwakIN.
Your response MUST always begin with: "If life is in danger, call 112"
Tone: calm, reassuring, urgent but not panicky.
Medical Rule: NEVER give medical diagnosis or medication dosage.

Your task is to take a government emergency alert and provide a plain-language summary and a list of actionable precautions.
You MUST provide the output in BOTH English and Hindi.
"""

    user_prompt = f"""Alert Title: {request.alert_title}
Alert Severity: {request.alert_severity}
Description: {request.alert_description}
Instructions: {request.alert_instruction}
"""

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        async def call_gemini():
            return await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "summary_en": {"type": "STRING"},
                            "precautions_en": {"type": "ARRAY", "items": {"type": "STRING"}},
                            "summary_hi": {"type": "STRING"},
                            "precautions_hi": {"type": "ARRAY", "items": {"type": "STRING"}}
                        },
                        "required": ["summary_en", "precautions_en", "summary_hi", "precautions_hi"]
                    },
                    temperature=0.2
                )
            )

        response = await asyncio.wait_for(call_gemini(), timeout=20.0)
        
        raw_json = response.text
        data = json.loads(raw_json)
        
        # Ensure the rule "If life is in danger, call 112" is at the top of the summary if not present
        if "call 112" not in data.get("summary_en", "").lower():
            data["summary_en"] = "If life is in danger, call 112. " + data.get("summary_en", "")
            
        if "112" not in data.get("summary_hi", ""):
            data["summary_hi"] = "यदि जीवन खतरे में है, तो 112 पर कॉल करें। " + data.get("summary_hi", "")
            
        return ExplainAlertResponse(**data)
        
    except Exception as e:
        logger.error(f"Gemini API error (explain alert): {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate alert explanation.")
