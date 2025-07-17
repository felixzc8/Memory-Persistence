from . import Base
from app.core.config import settings
from sqlalchemy import Column, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pytidb.schema import VectorField

class Memories(Base):
    __tablename__ = 'memories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vector: Mapped[list[float]] = mapped_column(VectorField(dimensions=settings.embedding_model_dims))
    payload: Mapped[JSON] = mapped_column(JSON)