from sqlalchemy import Column, String, Text, DateTime, JSON, Enum, ForeignKey, Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(Enum("user", "assistant", "system", name="message_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    session = relationship("Session", back_populates="messages")