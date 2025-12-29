import json
from nats.aio.client import Client as NATS
from app.config import config
from app.database.models.currency import CurrencyRate
from app.schemas.currency import CurrencyRateOut
from app.ws.connection_manager import manager
from app.schemas.ws_events import CurrencyEvent, CurrencyEventType
from app.database.session import async_session_factory
from datetime import datetime
from sqlalchemy import select






nc = NATS()

async def nats_connect():
    if not nc.is_connected:
        print("[NATS] Подключение к серверу NATS...")
        await nc.connect(config.NATS_URL)
        print(f"[NATS] Подключение установлено: {config.NATS_URL}")

        await nc.subscribe(config.NATS_SUBJECT, cb=nats_handler)
        print(f"[NATS] Подписка на канал: {config.NATS_SUBJECT}")


async def nats_close():
    "Отключение от натса"
    if nc.is_connected:
        await nc.close()

async def nats_publish(subject: str, data: dict):
    if not nc.is_connected:
        print("[NATS] Невозможно отправить сообщение: нет соединения")
        return

    await nc.publish(subject, json.dumps(data).encode())
    print(f"[NATS] Публикация сообщения в канал '{subject}': {data}")



async def nats_handler(msg):
    """Обработка сообщения"""
    try:
        data: dict = json.loads(msg.data.decode())
        print(f"[NATS] Получено сообщение из канала '{msg.subject}': {data}")
        timestamp = datetime.fromisoformat(data["timestamp"])

        if data.get("source") != "exchange_rate_parser":
            async with async_session_factory() as session:
                result = await session.execute(select(CurrencyRate).where(CurrencyRate.currency == data["currency"]))
                currency = result.scalars().first()
                
                if currency:
                    currency.rate = data["rate"]
                    currency.timestamp = timestamp
                else:
                    currency = CurrencyRate(
                        id=data["id"],
                        currency=data["currency"],
                        rate=data["rate"],
                        timestamp=timestamp
                    )
                    session.add(currency)
                
                await session.commit()
        
        event = CurrencyEvent(
            event_type=CurrencyEventType(data["event_type"]),
            currency=CurrencyRateOut(
                id=data["id"],
                currency=data["currency"],
                rate=data["rate"],
                timestamp=timestamp
            ),
            timestamp=timestamp
        )
        print("[WebSocket] Отправка события клиентам")
        await manager.broadcast(event)
        print("[WebSocket] Событие отправлено")
    except Exception as e:
        print(f"Error in nats_handler: {e}")