from datetime import datetime, timezone
from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import HTTPException

from schemas.review import Review, ReviewCreate, ReviewUpdate


class ReviewService:
    logger = logging.getLogger(__name__)

    @classmethod
    async def create_review(
        cls,
        review_data: ReviewCreate,
    ) -> Review:
        """Создает рецензию, если она не существует."""
        # Проверяем существование рецензии
        existing_review = await Review.find_one(
            Review.user_id == review_data.user_id,
            Review.filmwork_id == review_data.filmwork_id,
        )

        if existing_review:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Рецензия для этого фильма уже существует',
            )

        review = Review(
            user_id=review_data.user_id,
            filmwork_id=review_data.filmwork_id,
            text=review_data.text,
            author_name=review_data.author_name,
            rating=review_data.rating,
        )
        return await review.insert()

    @classmethod
    async def update_review(
        cls,
        review_id: UUID,
        review_data: ReviewUpdate,
    ) -> Review:
        """Обновляет рецензию."""
        review = await Review.get(review_id)

        if review is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        review.text = review_data.text
        review.author_name = review_data.author_name
        review.rating = review_data.rating
        review.updated_at = datetime.now(timezone.utc)

        await review.save()
        return review

    @classmethod
    async def delete_review(
        cls,
        review_id: UUID,
    ) -> Review:
        """Удаляет рецензию."""
        review = await Review.get(review_id)

        if review is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        await review.delete()
        return review

    @classmethod
    async def get_review(
        cls,
        review_id: UUID,
    ) -> Review:
        """Возвращает рецензию по ID."""
        review = await Review.get(review_id)

        if review is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        return review

    @classmethod
    async def get_filmwork_reviews(
        cls,
        filmwork_id: UUID,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = 'created_at',
    ) -> list[Review]:
        """Возвращает рецензии для кинопроизведения с сортировкой."""
        query = Review.find(Review.filmwork_id == filmwork_id)

        # Сортировка
        if sort_by == 'rating':
            query = query.sort(-Review.rating)  # type: ignore
        elif sort_by == 'created_at':
            query = query.sort(-Review.created_at)  # type: ignore
        else:
            query = query.sort(-Review.created_at)  # type: ignore

        return await query.skip(skip).limit(limit).to_list()

    @classmethod
    async def get_user_reviews(cls, user_id: UUID) -> list[Review]:
        """Возвращает все рецензии пользователя."""
        return await Review.find(
            Review.user_id == user_id,
        ).sort(-Review.created_at).to_list()  # type: ignore
