from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class ReviewLike(Document):
    """Лайк/дизлайк рецензии."""
    class Settings:
        name = 'review_likes'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('review_id', ASCENDING)],
                unique=True,
                name='unique_like_per_user_review',
            ),
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('review_id', ASCENDING)]),
            IndexModel([('is_like', ASCENDING)]),
            IndexModel([('created_at', ASCENDING)]),
        ]

    id: UUID = Field(default_factory=uuid4)  # type: ignore
    review_id: UUID
    user_id: UUID
    # True - лайк, False - дизлайк.
    is_like: bool
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


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


class Rating(Document):
    """Оценка кинопроизведения."""
    class Settings:
        name = 'ratings'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('filmwork_id', ASCENDING)],
                unique=True,
                name='unique_rating_per_user',
            ),
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('filmwork_id', ASCENDING)]),
            IndexModel([('rating', ASCENDING)]),
            IndexModel([('created_at', ASCENDING)]),
        ]

    id: UUID = Field(default_factory=uuid4)  # type: ignore
    filmwork_id: UUID
    user_id: UUID
    rating: int = Field(ge=0, le=10)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


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
