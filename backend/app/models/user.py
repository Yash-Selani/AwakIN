from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base

class User(Base):
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    photo_url = Column(String(1024))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
