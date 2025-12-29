import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, DateTime
from app.database.models.base import Base

class CurrencyRate(Base):
    """Модель базы данных - валюта"""
    __tablename__ = "currencies"
    #Уникальный идентификатор 
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    #Название
    currency: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    #Курс 
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    #Время изменения
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)