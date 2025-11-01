from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field, validator
from pymongo import ASCENDING, IndexModel


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
    rating: int = Field(ge=0, le=10)  # Оценка от 0 до 10
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class RatingCreate(BaseModel):
    """Модель для создания оценки."""
    filmwork_id: UUID
    user_id: UUID
    rating: int = Field(ge=0, le=10)

    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('Рейтинг должен быть от 0 до 10')
        return v


class RatingUpdate(BaseModel):
    """Модель для обновления оценки."""
    rating: int = Field(ge=0, le=10)

    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('Рейтинг должен быть от 0 до 10')
        return v


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
    likes_count: int = 0  # Количество оценок 10
    dislikes_count: int = 0  # Количество оценок 0
    ratings_count: int = 0
    ratings_distribution: dict[int, int] = Field(default_factory=dict)
