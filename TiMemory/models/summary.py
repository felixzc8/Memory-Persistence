from sqlalchemy import String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from tidb_vector.sqlalchemy import VectorType
from .memory import Base

class Summary(Base):
    __tablename__ = 'summaries'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey('sessions.session_id'), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector: Mapped[list[float]] = mapped_column(VectorType(dim=1536), nullable=False)
    message_count_at_creation: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    session = relationship("Session", back_populates="summaries")