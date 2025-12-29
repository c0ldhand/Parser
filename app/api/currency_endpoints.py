import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models.currency import CurrencyRate
from app.database.session import get_async_session
from app.nats.nats_events import publish_currency_event
from app.schemas.currency import CurrencyRateCreate, CurrencyRateOut, CurrencyRateUpdate
from datetime import datetime, timezone
from app.schemas.ws_events import CurrencyEventType

router = APIRouter(prefix="/currencies", tags=["currencies"])

@router.get("/", response_model=list[CurrencyRateOut])
async def get_currencies(session: AsyncSession = Depends(get_async_session)):
    """Получить список всех валют"""
    result = await session.execute(select(CurrencyRate))
    return result.scalars().all()


@router.get("/{currency_id}", response_model=CurrencyRateOut)
async def get_currency(currency_id: str, session: AsyncSession = Depends(get_async_session)):
    """Получить конкретную валюту по id"""
    currency = await session.get(CurrencyRate, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@router.post("/", response_model=CurrencyRateOut, status_code=status.HTTP_201_CREATED)
async def create_currency(currency_payload: CurrencyRateCreate, session: AsyncSession = Depends(get_async_session)):
    """Создать новую валюту"""
    currency = CurrencyRate(
        currency=currency_payload.currency,
        rate=currency_payload.rate,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(currency)
    await session.commit()
    await session.refresh(currency)
    await publish_currency_event(currency, CurrencyEventType.CREATED)

    return currency


@router.patch("/{currency_id}", response_model=CurrencyRateOut)
async def update_currency(currency_id: str, currency_payload: CurrencyRateUpdate, session: AsyncSession = Depends(get_async_session)):
    "Обновить курс валюту"
    currency = await session.get(CurrencyRate, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    currency.rate = currency_payload.rate
    currency.timestamp = datetime.now(timezone.utc)
    
    await session.commit()
    await session.refresh(currency)
    await publish_currency_event(currency, CurrencyEventType.UPDATED)

    return currency


@router.delete("/{currency_id}")
async def delete_currency(currency_id: str, session: AsyncSession = Depends(get_async_session)):
    """Удалить валюту"""
    currency = await session.get(CurrencyRate, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    await session.delete(currency)
    await session.commit()
    await publish_currency_event(currency, CurrencyEventType.DELETED)
    return {"status": "deleted"}