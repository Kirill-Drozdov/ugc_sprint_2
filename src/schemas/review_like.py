from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
