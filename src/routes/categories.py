"""
Завдання 4: CRUD endpoints для категорій
- GET    /api/categories/        — список категорій
- GET    /api/categories/{id}    — одна категорія
- POST   /api/categories/        — створити
- PUT    /api/categories/{id}    — оновити
- DELETE /api/categories/{id}    — видалити
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from settings import get_db
from src.repository import categories as repository_categories
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Отримати список усіх категорій."""
    return await repository_categories.get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Отримати категорію за ID."""
    category = await repository_categories.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з ID {category_id} не знайдено",
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Створити нову категорію.

    - **name**: унікальна назва категорії
    - **slug**: унікальний URL-slug (тільки латиниця, цифри, дефіс)
    - **description**: опис (необов'язково)
    """
    # Перевірка унікальності name
    if await repository_categories.get_category_by_name(db, category_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Категорія з назвою '{category_data.name}' вже існує",
        )
    # Перевірка унікальності slug
    if await repository_categories.get_category_by_slug(db, category_data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Категорія зі slug '{category_data.slug}' вже існує",
        )
    return await repository_categories.create_category(db, category_data)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Оновити категорію. Всі поля опціональні."""
    # Перевірка унікальності name якщо передали
    if category_data.name:
        existing = await repository_categories.get_category_by_name(db, category_data.name)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Назва '{category_data.name}' вже зайнята іншою категорією",
            )
    # Перевірка унікальності slug якщо передали
    if category_data.slug:
        existing = await repository_categories.get_category_by_slug(db, category_data.slug)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{category_data.slug}' вже зайнятий іншою категорією",
            )

    category = await repository_categories.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з ID {category_id} не знайдено",
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Видалити категорію за ID.

    Навички цієї категорії збережуться, але їх category_id стане NULL.
    """
    deleted = await repository_categories.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з ID {category_id} не знайдено",
        )
    return None
