from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BookmarkCreate(BaseModel):
    """Модель для создания закладки."""
    filmwork_id: UUID
    user_id: UUID


class BookmarkResponse(BaseModel):
    """Модель для ответа."""
    id: UUID
    filmwork_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
