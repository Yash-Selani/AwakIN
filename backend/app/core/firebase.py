import base64
import json
import logging
import os
import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Supports three methods (in priority order):
    1. JSON file path (local dev, when the file exists)
    2. Base64-encoded JSON env var (Vercel / serverless)
    3. Project ID only (token verification fallback)
    """
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        elif settings.FIREBASE_CREDENTIALS_JSON:
            try:
                raw_val = settings.FIREBASE_CREDENTIALS_JSON.strip()
                if raw_val.startswith("{"):
                    # Direct JSON string
                    cred_dict = json.loads(raw_val)
                else:
                    # Base64-encoded string
                    json_bytes = base64.b64decode(raw_val)
                    cred_dict = json.loads(json_bytes)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                logger.error(f"Failed to initialize Firebase from FIREBASE_CREDENTIALS_JSON: {e}")
                raise
        elif settings.FIREBASE_PROJECT_ID:
            firebase_admin.initialize_app(options={'projectId': settings.FIREBASE_PROJECT_ID})
        else:
            # Relies on GOOGLE_APPLICATION_CREDENTIALS if configured
            firebase_admin.initialize_app()
