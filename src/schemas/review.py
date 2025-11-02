from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.review_like import ReviewLikeSummary


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
    # TODO Оценку тут можно убрать.
    rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # Добавляем информацию о лайках.
    likes_count: int = 0
    dislikes_count: int = 0
    # Голос текущего пользователя.
    user_vote: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewWithLikesResponse(BaseModel):
    """Расширенная модель рецензии со статистикой лайков."""
    review: ReviewResponse
    like_summary: ReviewLikeSummary
