from sqlalchemy import Column, String, DateTime, Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
