from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.enum_models import ExchangeStatus


class ExchangeResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    skill_id: int
    message: Optional[str] = None
    status: ExchangeStatus
    hours_proposed: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
