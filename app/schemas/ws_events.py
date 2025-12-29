from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.schemas.currency import CurrencyRateOut

class CurrencyEventType(str, Enum):
    """Enum существующих типов ивентов"""
    CREATED = "currency_created"
    UPDATED = "currency_updated"
    DELETED = "currency_deleted"
    TASK_COMPLETED = "task_completed"
    ADD_DATA_FROM_REMOTE_SOURCE = "add_data_from_remote_source"

class CurrencyEvent(BaseModel):
    """Схема ивента"""
    event_type: CurrencyEventType
    currency: CurrencyRateOut
    timestamp: datetime

    model_config = {"from_attributes": True}