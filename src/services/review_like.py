from http import HTTPStatus
import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

from db.models import Review, ReviewLike
from schemas.review_like import ReviewLikeCreate, ReviewLikeSummary


class ReviewLikeService:
    logger = logging.getLogger(__name__)

    @classmethod
    async def create_or_update_review_like(
        cls,
        like_data: ReviewLikeCreate,
    ) -> ReviewLike:
        """Создает или обновляет лайк/дизлайк рецензии."""
        # Проверяем существование рецензии
        review = await Review.get(like_data.review_id)
        if review is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Рецензия не найдена',
            )

        # Проверяем существующий лайк
        existing_like = await ReviewLike.find_one(
            ReviewLike.user_id == like_data.user_id,
            ReviewLike.review_id == like_data.review_id,
        )

        if existing_like:
            # Обновляем существующий лайк
            existing_like.is_like = like_data.is_like
            await existing_like.save()
            return existing_like

        # Создаем новый лайк
        review_like = ReviewLike(
            review_id=like_data.review_id,
            user_id=like_data.user_id,
            is_like=like_data.is_like,
        )
        return await review_like.insert()

    @classmethod
    async def delete_review_like(
        cls,
        user_id: UUID,
        review_id: UUID,
    ) -> Optional[ReviewLike]:
        """Удаляет лайк/дизлайк рецензии."""
        review_like = await ReviewLike.find_one(
            ReviewLike.user_id == user_id,
            ReviewLike.review_id == review_id,
        )

        if review_like is None:
            return None

        await review_like.delete()
        return review_like

    @classmethod
    async def get_review_like_summary(
        cls,
        review_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> ReviewLikeSummary:
        """Возвращает сводную информацию по лайкам рецензии."""
        # Получаем все лайки для рецензии
        likes = await ReviewLike.find(
            ReviewLike.review_id == review_id,
            ReviewLike.is_like is True,
        ).to_list()

        dislikes = await ReviewLike.find(
            ReviewLike.review_id == review_id,
            ReviewLike.is_like is False,
        ).to_list()

        # Определяем голос текущего пользователя
        user_vote = None
        if user_id:
            user_like = await ReviewLike.find_one(
                ReviewLike.user_id == user_id,
                ReviewLike.review_id == review_id,
            )
            if user_like:
                user_vote = user_like.is_like

        return ReviewLikeSummary(
            review_id=review_id,
            likes_count=len(likes),
            dislikes_count=len(dislikes),
            user_vote=user_vote,
        )

    @classmethod
    async def get_user_review_likes(cls, user_id: UUID) -> list[ReviewLike]:
        """Возвращает все лайки пользователя."""
        return await ReviewLike.find(
            ReviewLike.user_id == user_id,
        ).to_list()
