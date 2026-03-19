"""
Завдання 4: Repository для категорій — повний CRUD
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Category
from src.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    """Отримати список усіх категорій."""
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.scalars(stmt)
    return result.all()


async def get_category(db: AsyncSession, category_id: int) -> Optional[Category]:
    """Отримати категорію за ID."""
    return await db.scalar(select(Category).where(Category.id == category_id))


async def get_category_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
    """Отримати категорію за slug."""
    return await db.scalar(select(Category).where(Category.slug == slug))


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[Category]:
    """Перевірити чи існує категорія з такою назвою."""
    return await db.scalar(select(Category).where(Category.name == name))


async def create_category(db: AsyncSession, category_data: CategoryCreate) -> Category:
    """Створити нову категорію."""
    db_category = Category(**category_data.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def update_category(
    db: AsyncSession, category_id: int, category_data: CategoryUpdate
) -> Optional[Category]:
    """Оновити категорію. Повертає None якщо не знайдено."""
    db_category = await get_category(db, category_id)
    if not db_category:
        return None

    update_fields = category_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(db_category, field, value)

    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    """Видалити категорію. Повертає True якщо видалено, False якщо не знайдено."""
    db_category = await get_category(db, category_id)
    if not db_category:
        return False
    await db.delete(db_category)
    await db.commit()
    return True
