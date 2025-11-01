from datetime import datetime, timezone
from http import HTTPStatus
import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

from db.models import Rating
from schemas.rating import (
    FilmworkRatingSummary,
    RatingCreate,
    RatingUpdate,
)


class RatingService:
    logger = logging.getLogger(__name__)

    @classmethod
    async def create_rating(
        cls,
        rating_data: RatingCreate,
    ) -> Rating:
        """Создает новую оценку кинопроизведения."""
        # Проверяем существование оценки
        existing_rating = await Rating.find_one(
            Rating.user_id == rating_data.user_id,
            Rating.filmwork_id == rating_data.filmwork_id,
        )

        if existing_rating:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Оценка для этого фильма уже существует',
            )

        # Создаем новую оценку
        rating = Rating(
            user_id=rating_data.user_id,
            filmwork_id=rating_data.filmwork_id,
            rating=rating_data.rating,
        )
        return await rating.insert()

    @classmethod
    async def update_rating(
        cls,
        user_id: UUID,
        rating_id: UUID,
        rating_data: RatingUpdate,
    ) -> Rating:
        """Обновляет существующую оценку."""
        rating = await Rating.find_one(
            Rating.user_id == user_id,
            Rating.id == rating_id,
        )

        if rating is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Оценка не найдена',
            )

        rating.rating = rating_data.rating
        rating.updated_at = datetime.now(timezone.utc)
        await rating.save()
        return rating

    @classmethod
    async def get_user_rating(
        cls,
        user_id: UUID,
        filmwork_id: UUID,
    ) -> Optional[Rating]:
        """Возвращает оценку пользователя для кинопроизведения."""
        return await Rating.find_one(
            Rating.user_id == user_id,
            Rating.filmwork_id == filmwork_id,
        )

    @classmethod
    async def delete_rating(
        cls,
        user_id: UUID,
        filmwork_id: UUID,
    ) -> Optional[Rating]:
        """Удаляет оценку пользователя."""
        rating = await Rating.find_one(
            Rating.user_id == user_id,
            Rating.filmwork_id == filmwork_id,
        )

        if rating is None:
            return None

        await rating.delete()
        return rating

    @classmethod
    async def get_filmwork_rating_summary(
        cls,
        filmwork_id: UUID,
    ) -> FilmworkRatingSummary:
        """Возвращает сводную информацию по рейтингам кинопроизведения."""
        ratings = await Rating.find(
            Rating.filmwork_id == filmwork_id,
        ).to_list()

        if not ratings:
            return FilmworkRatingSummary(filmwork_id=filmwork_id)

        total_ratings = len(ratings)
        total_score = sum(r.rating for r in ratings)
        average_rating = round(total_score / total_ratings, 2)

        # Распределение оценок.
        distribution = {}
        for i in range(11):
            distribution[i] = sum(1 for r in ratings if r.rating == i)

        return FilmworkRatingSummary(
            filmwork_id=filmwork_id,
            average_rating=average_rating,
            # Оценки 10 считаем лайками.
            likes_count=distribution[10],
            # Оценки 0 считаем дизлайками.
            dislikes_count=distribution[0],
            ratings_count=total_ratings,
        )

    @classmethod
    async def get_user_ratings(cls, user_id: UUID) -> list[Rating]:
        """Возвращает все оценки пользователя."""
        return await Rating.find(
            Rating.user_id == user_id,
        ).sort(-Rating.updated_at).to_list()  # type: ignore
