from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CurrencyRateBase(BaseModel):
    """Базовый класс валюты"""
    currency: str
    rate: float

class CurrencyRateCreate(CurrencyRateBase):
    """Схема для создания валюты"""
    pass

class CurrencyRateUpdate(BaseModel):
    """Схема обновления курса валюты"""
    rate: float

class CurrencyRateOut(CurrencyRateBase):
    """Схема вывода"""
    id: UUID
    timestamp: datetime

    model_config = {"from_attributes": True}