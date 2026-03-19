"""
Завдання 3: Repository для exchanges з фільтрацією
- За датою (from_date, to_date)
- За статусом та користувачем одночасно
- Сортування за датою (asc/desc)
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.enum_models import ExchangeStatus
from src.models import Exchange


async def get_exchanges_filtered(
    db: AsyncSession,
    # Фільтр за датою
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    # Фільтр за статусом і юзером
    status: Optional[ExchangeStatus] = None,
    user_id: Optional[int] = None,
    # Сортування
    sort: str = "desc",
    # Пагінація
    skip: int = 0,
    limit: int = 20,
) -> List[Exchange]:
    """
    Отримати список обмінів з фільтрацією та сортуванням.

    - from_date / to_date: фільтр за created_at
    - status: фільтр за статусом обміну
    - user_id: фільтр — показати обміни де юзер є відправником АБО отримувачем
    - sort: 'asc' або 'desc' за датою створення
    """
    stmt = select(Exchange)

    # Фільтр за датою
    if from_date:
        stmt = stmt.where(Exchange.created_at >= from_date)
    if to_date:
        stmt = stmt.where(Exchange.created_at <= to_date)

    # Фільтр за статусом
    if status:
        stmt = stmt.where(Exchange.status == status)

    # Фільтр за юзером (відправник або отримувач)
    if user_id:
        stmt = stmt.where(
            (Exchange.sender_id == user_id) | (Exchange.receiver_id == user_id)
        )

    # Сортування
    if sort.lower() == "asc":
        stmt = stmt.order_by(asc(Exchange.created_at))
    else:
        stmt = stmt.order_by(desc(Exchange.created_at))

    # Пагінація
    stmt = stmt.offset(skip).limit(limit)

    result = await db.scalars(stmt)
    return result.all()


async def get_exchange_by_id(db: AsyncSession, exchange_id: int) -> Optional[Exchange]:
    """Отримати обмін за ID."""
    result = await db.scalar(select(Exchange).where(Exchange.id == exchange_id))
    return result
