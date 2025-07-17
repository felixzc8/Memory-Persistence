from sqlalchemy import Column, String, DateTime, Boolean, Mapped, mapped_column
from sqlalchemy.sql import func
from . import Base

class User(Base):
    """User model for the users table"""
    __tablename__ = 'users'
    
    user_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}')>"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }