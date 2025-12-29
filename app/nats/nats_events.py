from datetime import datetime, timezone
from app.nats.client import nats_publish
from app.config import config
from app.database.models.currency import CurrencyRate
from app.schemas.ws_events import CurrencyEventType

async def publish_currency_event(
        currency: CurrencyRate, event_type: CurrencyEventType, 
        source: str = "exchange_rate_parser"
        ):
    """Метод публикации ивентов для вебсокета"""
    await nats_publish(
        config.NATS_SUBJECT,
        {
            "id": str(currency.id),
            "currency": currency.currency,
            "rate": currency.rate,
            "event_type": event_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source
        }
    )
