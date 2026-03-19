from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Назва категорії")
    description: Optional[str] = Field(None, description="Опис категорії")
    slug: str = Field(..., min_length=2, max_length=50, description="URL-slug категорії")

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v):
        if v:
            v = v.strip().lower().replace(" ", "-")
            if not all(c.isalnum() or c == "-" for c in v):
                raise ValueError("Slug може містити лише літери, цифри та дефіс")
        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=2, max_length=50)


class CategoryResponse(CategoryBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
