from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class DisasterType(Base):
    __tablename__ = "disaster_types"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon = Column(String(100))
    severity_note = Column(String(255))
    
    guides = relationship("DisasterGuide", back_populates="disaster_type", cascade="all, delete-orphan")


class DisasterGuide(Base):
    __tablename__ = "disaster_guides"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    disaster_type_id = Column(String(36), ForeignKey("disaster_types.id"), nullable=False, unique=True)
    before_steps = Column(JSONB)
    during_steps = Column(JSONB)
    after_steps = Column(JSONB)
    first_aid = Column(JSONB)
    
    disaster_type = relationship("DisasterType", back_populates="guides")
