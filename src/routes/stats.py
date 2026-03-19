"""
Завдання 2: Статистичні endpoints
- GET /api/stats/top-skills
- GET /api/stats/active-users
- GET /api/stats/exchange-success-rate
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from settings import get_db
from src.repository import stats as repository_stats

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("/top-skills")
async def top_skills(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Топ найпопулярніших навичок за кількістю користувачів.

    - **limit**: кількість навичок у відповіді (за замовчуванням 10)
    """
    data = await repository_stats.get_top_skills(db, limit=limit)
    return {
        "description": "Топ навичок за кількістю користувачів",
        "count": len(data),
        "skills": data,
    }


@router.get("/active-users")
async def active_users(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Найактивніші користувачі за загальною кількістю обмінів.

    - **limit**: кількість користувачів у відповіді (за замовчуванням 10)
    """
    data = await repository_stats.get_active_users(db, limit=limit)
    return {
        "description": "Найактивніші користувачі за кількістю обмінів",
        "count": len(data),
        "users": data,
    }


@router.get("/exchange-success-rate")
async def exchange_success_rate(db: AsyncSession = Depends(get_db)):
    """
    Відсоток успішних обмінів (статус completed).

    Повертає загальну кількість обмінів, success rate у відсотках
    та розбивку по кожному статусу.
    """
    data = await repository_stats.get_exchange_success_rate(db)
    return data
