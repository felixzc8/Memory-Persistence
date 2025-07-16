from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")