from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, IndexModel


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


class ReviewLikeCreate(BaseModel):
    """Модель для создания лайка/дизлайка рецензии."""
    review_id: UUID
    user_id: UUID
    is_like: bool


class ReviewLikeResponse(BaseModel):
    """Модель для ответа."""
    id: UUID
    review_id: UUID
    user_id: UUID
    is_like: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewLikeSummary(BaseModel):
    """Сводная информация по лайкам рецензии."""
    review_id: UUID
    likes_count: int = 0
    dislikes_count: int = 0
    # True - лайк, False - дизлайк, None - нет голоса.
    user_vote: bool | None = None
