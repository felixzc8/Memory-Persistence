from sqlalchemy import Column, String, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", "system", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    session = relationship("Session", back_populates="messages")