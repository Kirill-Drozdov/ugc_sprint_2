from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter

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
) -> ReviewLike:
    """Добавление лайка или дизлайка рецензии.

    - **review_id**: идентификатор рецензии.
    - **user_id**: идентификатор пользователя.
    - **is_like**: True - лайк, False - дизлайк.
    """
    return await ReviewLikeService.create_or_update_review_like(like_data)


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
) -> ReviewLikeSummary:
    """Получение статистики лайков рецензии.

    - **review_id**: идентификатор рецензии.
    - **likes_count**: число лайков.
    - **dislikes_count**: число дизлайков.
    - **user_vote**: оценка пользователя.
    """
    return await ReviewLikeService.get_review_like_summary(
        review_id,
        user_id,
    )


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
) -> ReviewLike:
    """Удаление лайка или дизлайка рецензии.

    - **id**: идентификатор лайка рецензии.
    - **review_id**: идентификатор рецензии.
    - **user_id**: идентификатор пользователя.
    - **is_like**: лайк или не лайк.
    - **created_at**: дата созданияы.
    """
    return await ReviewLikeService.delete_review_like(
        user_id,
        review_id,
    )
