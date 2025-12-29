from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_async_session
from app.tasks.cbr_rates import generate_cbr_rates


router = APIRouter(prefix="/tasks", tags=["background"])

@router.post("/run")
async def run_cbr_task(
    background_tasks: BackgroundTasks, session:
    AsyncSession = Depends(get_async_session)
    ):
    """
    Принудительный запуск фоновой задачи
    """
    background_tasks.add_task(generate_cbr_rates, session)
    return {"status": "started"}