from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field
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
    # Оценка в рецензии (опционально)
    rating: Optional[int] = Field(None, ge=0, le=10)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
