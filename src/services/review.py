import asyncio
from datetime import datetime, timezone
from http import HTTPStatus
import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

from db.models import Review
from schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from services.review_like import ReviewLikeService


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
        user_id: UUID,
        review_id: UUID,
    ) -> ReviewResponse:
        """Удаляет рецензию."""
        review = await cls.get_review(review_id, user_id)
        review_to_remove = await Review.get(review_id)

        if review_to_remove is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        await review_to_remove.delete()
        return review  # noqa

    @classmethod
    async def get_review(
        cls,
        review_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> ReviewResponse:
        """Возвращает рецензию по ID с информацией о лайках."""
        review = await Review.get(review_id)

        if review is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        # Получаем информацию о лайках
        like_summary = await ReviewLikeService.get_review_like_summary(
            review_id,
            user_id,
        )

        return ReviewResponse(
            **review.dict(),
            likes_count=like_summary.likes_count,
            dislikes_count=like_summary.dislikes_count,
            user_vote=like_summary.user_vote,
        )

    @classmethod
    async def get_filmwork_reviews(
        cls,
        filmwork_id: UUID,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = 'created_at',
    ) -> list[ReviewResponse]:
        """Возвращает рецензии для кинопроизведения с сортировкой."""
        query = Review.find(Review.filmwork_id == filmwork_id)

        # Сортировка
        if sort_by == 'rating':
            query = query.sort(-Review.rating)  # type: ignore
        elif sort_by == 'created_at':
            query = query.sort(-Review.created_at)  # type: ignore
        else:
            query = query.sort(-Review.created_at)  # type: ignore

        reviews = await query.skip(skip).limit(limit).to_list()

        tasks = [
            ReviewLikeService.get_review_like_summary(review.id, user_id)
            for review in reviews
        ]

        like_summaries = await asyncio.gather(*tasks)

        return [
            ReviewResponse(
                **review.dict(),
                likes_count=summary.likes_count,
                dislikes_count=summary.dislikes_count,
                user_vote=summary.user_vote,
            )
            for review, summary in zip(reviews, like_summaries)
        ]

    @classmethod
    async def get_user_reviews(
        cls,
        user_id: UUID,
    ) -> list[ReviewResponse]:
        """Возвращает все рецензии пользователя."""
        reviews = await Review.find(
            Review.user_id == user_id,
        ).sort(-Review.created_at).to_list()  # type: ignore

        tasks = [
            ReviewLikeService.get_review_like_summary(review.id, user_id)
            for review in reviews
        ]

        like_summaries = await asyncio.gather(*tasks)

        return [
            ReviewResponse(
                **review.dict(),
                likes_count=summary.likes_count,
                dislikes_count=summary.dislikes_count,
                user_vote=summary.user_vote,
            )
            for review, summary in zip(reviews, like_summaries)
        ]
