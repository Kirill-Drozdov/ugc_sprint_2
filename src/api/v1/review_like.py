from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from db.models import ReviewLike
from schemas.review_like import (
    ReviewLikeCreate,
    ReviewLikeResponse,
    ReviewLikeSummary,
)
from services.review_like import ReviewLikeService

router = APIRouter()


@router.post(
    '/',
    response_model=ReviewLikeResponse,
    summary='Добавление лайка/дизлайка рецензии',
    response_description='Информация по лайку/дизлайку',
    status_code=HTTPStatus.CREATED,
)
async def create_or_update_review_like(
    like_data: ReviewLikeCreate,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewLike:
    """Добавление лайка или дизлайка рецензии.

    - **review_id**: идентификатор рецензии.
    - **user_id**: идентификатор пользователя.
    - **is_like**: True - лайк, False - дизлайк.
    """
    try:
        return await ReviewLikeService.create_or_update_review_like(like_data)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при добавлении лайка/дизлайка: {error}')
        raise


@router.get(
    '/review/{review_id}/summary',
    response_model=ReviewLikeSummary,
    summary='Получение статистики лайков рецензии',
    response_description='Статистика лайков рецензии',
    status_code=HTTPStatus.OK,
)
async def get_review_like_summary(
    review_id: UUID,
    # TODO Получать через авторизацию JWT.
    user_id: UUID | None = None,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewLikeSummary:
    """Получение статистики лайков рецензии.

    - **review_id**: идентификатор рецензии.
    - **likes_count**: число лайков.
    - **dislikes_count**: число дизлайков.
    - **user_vote**: оценка пользователя.
    """
    try:
        return await ReviewLikeService.get_review_like_summary(
            review_id,
            user_id,
        )
    except Exception as error:
        logger.error(f'Ошибка при получении статистики лайков: {error}')
        raise


@router.delete(
    '/user/{user_id}/review/{review_id}',
    response_model=ReviewLikeResponse,
    summary='Удаление лайка/дизлайка рецензии',
    response_description='Информация по удаленному лайку/дизлайку',
    status_code=HTTPStatus.OK,
)
async def delete_review_like(
    user_id: UUID,
    review_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewLike:
    """Удаление лайка или дизлайка рецензии.

    - **id**: идентификатор лайка рецензии.
    - **review_id**: идентификатор рецензии.
    - **user_id**: идентификатор пользователя.
    - **is_like**: лайк или не лайк.
    - **created_at**: дата созданияы.
    """
    try:
        review_like = await ReviewLikeService.delete_review_like(
            user_id,
            review_id,
        )
        if review_like is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Лайк/дизлайк не найден',
            )
        return review_like
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при удалении лайка/дизлайка: {error}')
        raise
