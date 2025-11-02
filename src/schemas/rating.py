from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, validator


class RatingCreate(BaseModel):
    """Модель для создания оценки."""
    filmwork_id: UUID
    user_id: UUID
    rating: int = Field(ge=0, le=10)

    @validator('rating')
    def validate_rating(cls, rating):
        if not 0 <= rating <= 10:
            raise ValueError('Рейтинг должен быть от 0 до 10')
        return rating


class RatingUpdate(BaseModel):
    """Модель для обновления оценки."""
    rating: int = Field(ge=0, le=10)

    @validator('rating')
    def validate_rating(cls, rating):
        if not 0 <= rating <= 10:
            raise ValueError('Рейтинг должен быть от 0 до 10')
        return rating


class RatingResponse(BaseModel):
    """Модель для ответа."""
    id: UUID
    filmwork_id: UUID
    user_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FilmworkRatingSummary(BaseModel):
    """Сводная информация по рейтингам кинопроизведения."""
    filmwork_id: UUID
    average_rating: Optional[float] = None
    likes_count: int = 0
    dislikes_count: int = 0
    ratings_count: int = 0
