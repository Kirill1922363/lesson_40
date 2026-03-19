"""
Завдання 3: Endpoints для exchanges з фільтрацією
- GET /api/exchanges/ — список з фільтрами за датою, статусом, юзером
"""
from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from settings import get_db
from src.enum_models import ExchangeStatus
from src.repository import exchanges as repository_exchanges
from src.schemas.exchange import ExchangeResponse

router = APIRouter(prefix="/api/exchanges", tags=["Exchanges"])


@router.get("/", response_model=List[ExchangeResponse])
async def get_exchanges(
    # Фільтр за датою
    from_date: Optional[datetime] = Query(
        None,
        description="Від якої дати (ISO формат, напр. 2026-01-01T00:00:00)",
        example="2026-01-01T00:00:00",
    ),
    to_date: Optional[datetime] = Query(
        None,
        description="До якої дати (ISO формат)",
        example="2026-12-31T23:59:59",
    ),
    # Фільтр за статусом та юзером
    status: Optional[ExchangeStatus] = Query(None, description="Статус обміну"),
    user_id: Optional[int] = Query(None, description="ID користувача (відправник або отримувач)"),
    # Сортування
    sort: Literal["asc", "desc"] = Query("desc", description="Сортування за датою: asc або desc"),
    # Пагінація
    skip: int = Query(0, ge=0, description="Пропустити N записів"),
    limit: int = Query(20, ge=1, le=100, description="Максимум записів у відповіді"),
    db: AsyncSession = Depends(get_db),
):
    """
    Отримати список обмінів з фільтрацією.

    Фільтри можна комбінувати:
    - **from_date** / **to_date**: діапазон дат створення
    - **status**: pending / accepted / rejected / completed / cancelled
    - **user_id**: показати обміни де цей юзер є відправником АБО отримувачем
    - **sort**: asc (старіші спочатку) або desc (новіші спочатку)
    """
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date не може бути пізніше ніж to_date",
        )

    exchanges = await repository_exchanges.get_exchanges_filtered(
        db,
        from_date=from_date,
        to_date=to_date,
        status=status,
        user_id=user_id,
        sort=sort,
        skip=skip,
        limit=limit,
    )
    return exchanges


@router.get("/{exchange_id}", response_model=ExchangeResponse)
async def get_exchange(exchange_id: int, db: AsyncSession = Depends(get_db)):
    """Отримати обмін за ID."""
    exchange = await repository_exchanges.get_exchange_by_id(db, exchange_id)
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обмін з ID {exchange_id} не знайдено",
        )
    return exchange
