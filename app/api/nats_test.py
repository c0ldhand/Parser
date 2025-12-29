from fastapi import APIRouter
from app.nats.client import nats_publish
from app.config import config
from datetime import datetime, timezone
from app.schemas.ws_events import CurrencyEventType
from uuid import uuid4

router = APIRouter()

@router.post("/test/nats", tags=["test"])
async def test_nats_message(currency: str = "USD", rate: float = 100.0):
    """Ручка имитирующая запрос с другого сервиса"""
    await nats_publish(config.NATS_SUBJECT, {
        "id": str(uuid4()),
        "currency": currency,
        "rate": rate,
        "event_type": CurrencyEventType.ADD_DATA_FROM_REMOTE_SOURCE.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "test"
    })
    return {"status": "ok"}
