from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class Review(Document):
    """Рецензия на кинопроизведение."""
    class Settings:
        name = 'reviews'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('filmwork_id', ASCENDING)],
                unique=True,
                name='unique_review_per_user',
            ),
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('filmwork_id', ASCENDING)]),
            IndexModel([('created_at', DESCENDING)]),
            IndexModel([('rating', DESCENDING)]),
        ]

    id: UUID = Field(default_factory=uuid4)  # type: ignore
    filmwork_id: UUID
    user_id: UUID
    text: str
    author_name: str  # Имя автора рецензии
    rating: Optional[int] = Field(None, ge=0, le=10)  # Оценка в рецензии (опционально)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class ReviewCreate(BaseModel):
    """Модель для создания рецензии."""
    filmwork_id: UUID
    user_id: UUID
    text: str
    author_name: str
    rating: Optional[int] = Field(None, ge=0, le=10)


class ReviewUpdate(BaseModel):
    """Модель для обновления рецензии."""
    text: str
    author_name: str
    rating: Optional[int] = Field(None, ge=0, le=10)


class ReviewResponse(BaseModel):
    """Модель для ответа."""
    id: UUID
    filmwork_id: UUID
    user_id: UUID
    text: str
    author_name: str
    rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)