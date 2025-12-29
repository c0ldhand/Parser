import asyncio
import httpx
import xml.etree.ElementTree as ET
from app.database.models.currency import CurrencyRate
from datetime import datetime, timezone
from app.nats.nats_events import publish_currency_event
from app.schemas.ws_events import CurrencyEventType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_async_session


SLEEP_TIME = 3600


async def fetch_cbr_rates() -> list[dict]:
    """Получение  курса валют с сайта ЦБ РФ и обработка"""
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        xml_root = ET.fromstring(resp.text)

    rates = []
    for valute in xml_root.findall("Valute"):
        char_elem = valute.find("CharCode")
        value_elem = valute.find("Value")
        nominal_elem = valute.find("Nominal")

        if char_elem is None or value_elem is None or nominal_elem is None:
            continue

        char_code = char_elem.text
        value_text = value_elem.text
        nominal_text = nominal_elem.text

        if not char_code or not value_text or not nominal_text:
            continue

        nominal = int(nominal_text)
        rate = float(value_text.replace(",", ".")) / nominal

        rates.append({
            "currency": char_code,
            "rate": rate
        })

    return rates


async def generate_cbr_rates(session: AsyncSession):
    "Обновление данных в бд по данным из ЦБ РФ"
    data = await fetch_cbr_rates()
    for item in data:
        result = await session.execute(select(CurrencyRate).where(CurrencyRate.currency == item["currency"]))
        currency = result.scalars().first()
        
        if not currency:
            currency = CurrencyRate(
                currency=item["currency"],
                rate=item["rate"],
                timestamp=datetime.now(timezone.utc)
            )
            session.add(currency)
            event_type = CurrencyEventType.CREATED
        else:
            if currency.rate != item["rate"]:
                currency.rate = item["rate"]
                currency.timestamp = datetime.now(timezone.utc)
                event_type = CurrencyEventType.UPDATED
            else:
                continue

        await session.commit()
        await session.refresh(currency)
        await publish_currency_event(currency, event_type)


async def periodic_task():
    """Вызов переодической задачи"""
    try:
        while True:
            async for session in get_async_session():
                try:
                    await generate_cbr_rates(session)
                except Exception as e:
                    print("Ошибка при обработке курса ЦБ:", e)
            await asyncio.sleep(SLEEP_TIME)
    except asyncio.CancelledError:
        pass