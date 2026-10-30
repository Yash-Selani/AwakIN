import asyncio
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to verify Firebase ID token and return the current user.
    If the user doesn't exist in the database, it creates a new record.
    External call to Firebase is wrapped with a timeout.
    """
    token = credentials.credentials
    try:
        # Wrap the external API call with a 5.0s timeout
        decoded_token = await asyncio.wait_for(
            asyncio.to_thread(auth.verify_id_token, token),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        logger.error("Timeout verifying Firebase ID token")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Authentication service timeout"
        )
    except Exception as e:
        logger.error(f"Error verifying Firebase ID token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name")
    photo_url = decoded_token.get("picture")
    
    if not firebase_uid or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Check if user exists in the database
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()
    
    if not user:
        # Create a new user record
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            photo_url=photo_url
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user"
            )
            
    return user
