import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    # Завдання 1: нові поля
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL аватару користувача")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефону")
    location: Optional[str] = Field(None, max_length=100, description="Місто або країна")

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            v = v.strip()
            if v and not v.replace("+", "").replace("-", "").replace(" ", "").isdigit():
                raise ValueError("Невірний формат номера телефону")
        return v


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    # Завдання 1: оновлення нових полів
    avatar_url: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
