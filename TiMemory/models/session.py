from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .memory import Base

class Session(Base):
    __tablename__ = "sessions"
    
    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_activity: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    last_summary_message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
