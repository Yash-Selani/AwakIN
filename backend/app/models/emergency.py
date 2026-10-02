from sqlalchemy import Column, String
import uuid

from app.db.base_class import Base

class EmergencyNumber(Base):
    __tablename__ = "emergency_numbers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String(255), nullable=False)
    number = Column(String(50), nullable=False)
    category = Column(String(100), index=True)
    description = Column(String(500))
    region = Column(String(10), default="IN", index=True)


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    description = Column(String(1000))
    phone = Column(String(100))
    website = Column(String(255))
    state = Column(String(100), nullable=True, index=True)
