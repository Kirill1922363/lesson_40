"""
Завдання 2: Repository для статистичних endpoints
- топ-10 популярних навичок
- найактивніші користувачі
- відсоток успішних обмінів
"""
from typing import List

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.enum_models import ExchangeStatus
from src.models import Exchange, Skill, User, skill_user_association


async def get_top_skills(db: AsyncSession, limit: int = 10) -> List[dict]:
    """
    Топ-10 популярних навичок за кількістю користувачів.
    Рахуємо через skill_user_association скільки юзерів має кожну навичку.
    """
    stmt = (
        select(
            Skill.id,
            Skill.title,
            Skill.category,
            Skill.level,
            func.count(skill_user_association.c.user_id).label("user_count"),
        )
        .join(skill_user_association, Skill.id == skill_user_association.c.skill_id, isouter=True)
        .group_by(Skill.id, Skill.title, Skill.category, Skill.level)
        .order_by(desc("user_count"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "rank": idx + 1,
            "id": row.id,
            "title": row.title,
            "category": row.category,
            "level": row.level,
            "user_count": row.user_count,
        }
        for idx, row in enumerate(rows)
    ]


async def get_active_users(db: AsyncSession, limit: int = 10) -> List[dict]:
    """
    Найактивніші користувачі за загальною кількістю обмінів
    (відправлених + отриманих).
    """
    sent_subq = (
        select(Exchange.sender_id.label("user_id"), func.count(Exchange.id).label("sent"))
        .group_by(Exchange.sender_id)
        .subquery()
    )
    received_subq = (
        select(Exchange.receiver_id.label("user_id"), func.count(Exchange.id).label("received"))
        .group_by(Exchange.receiver_id)
        .subquery()
    )

    stmt = (
        select(
            User.id,
            User.username,
            User.full_name,
            User.location,
            func.coalesce(sent_subq.c.sent, 0).label("sent_count"),
            func.coalesce(received_subq.c.received, 0).label("received_count"),
            (func.coalesce(sent_subq.c.sent, 0) + func.coalesce(received_subq.c.received, 0)).label("total"),
        )
        .outerjoin(sent_subq, User.id == sent_subq.c.user_id)
        .outerjoin(received_subq, User.id == received_subq.c.user_id)
        .order_by(desc("total"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "rank": idx + 1,
            "id": row.id,
            "username": row.username,
            "full_name": row.full_name,
            "location": row.location,
            "sent_exchanges": row.sent_count,
            "received_exchanges": row.received_count,
            "total_exchanges": row.total,
        }
        for idx, row in enumerate(rows)
    ]


async def get_exchange_success_rate(db: AsyncSession) -> dict:
    """
    Відсоток успішних обмінів (status = completed).
    Повертає загальну статистику по всіх статусах.
    """
    # Загальна кількість
    total_stmt = select(func.count(Exchange.id))
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0

    # По кожному статусу
    by_status_stmt = (
        select(Exchange.status, func.count(Exchange.id).label("count"))
        .group_by(Exchange.status)
    )
    by_status_result = await db.execute(by_status_stmt)
    status_rows = by_status_result.all()

    status_counts = {row.status.value: row.count for row in status_rows}
    completed = status_counts.get(ExchangeStatus.completed.value, 0)
    success_rate = round((completed / total * 100), 2) if total > 0 else 0.0

    return {
        "total_exchanges": total,
        "success_rate_percent": success_rate,
        "by_status": {
            "pending": status_counts.get("pending", 0),
            "accepted": status_counts.get("accepted", 0),
            "rejected": status_counts.get("rejected", 0),
            "completed": completed,
            "cancelled": status_counts.get("cancelled", 0),
        },
    }
