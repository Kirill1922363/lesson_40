"""add user profile fields

Revision ID: e1a2b3c4d5e6
Revises: 4853c1c90588
Create Date: 2026-03-19 12:00:00.000000

Завдання 1: Додаємо поля avatar_url, phone, location до таблиці users
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "4853c1c90588"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Додати нові поля профілю до таблиці users."""
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("location", sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Видалити поля профілю з таблиці users."""
    op.drop_column("users", "location")
    op.drop_column("users", "phone")
    op.drop_column("users", "avatar_url")
