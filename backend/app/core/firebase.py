import firebase_admin
from firebase_admin import credentials
from app.core.config import settings

def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Uses credentials path if provided, otherwise uses project ID for token verification.
    """
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        elif settings.FIREBASE_PROJECT_ID:
            firebase_admin.initialize_app(options={'projectId': settings.FIREBASE_PROJECT_ID})
        else:
            # If neither is provided, initialize without arguments, 
            # which relies on GOOGLE_APPLICATION_CREDENTIALS
            firebase_admin.initialize_app()
