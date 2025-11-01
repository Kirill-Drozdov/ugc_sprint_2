from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, IndexModel


class Bookmark(Document):
    """Закладка."""
    class Settings:
        name = 'bookmarks'
        indexes = [
            # Уникальный составной индекс - предотвращает
            # дубликаты на уровне БД.
            IndexModel(
                [('user_id', ASCENDING), ('filmwork_id', ASCENDING)],
                unique=True,
                name='unique_bookmark_per_user',
            ),
            # Отдельные индексы для производительности
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('filmwork_id', ASCENDING)]),
            IndexModel([('created_at', ASCENDING)]),
        ]

    id: UUID = Field(default_factory=uuid4)  # type: ignore
    filmwork_id: UUID
    user_id: UUID
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),

    )


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
