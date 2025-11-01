from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from services.review import ReviewService

router = APIRouter()


@router.post(
    '/',
    response_model=ReviewResponse,
    summary='Создание рецензии',
    response_description='Информация по рецензии',
    status_code=HTTPStatus.CREATED,
)
async def create_review(
    review: ReviewCreate,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewResponse:
    """Создание рецензии на кинопроизведение.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **text**: текст рецензии.
    - **author_name**: имя автора.
    - **rating**: оценка от 0 до 10 (опционально).
    """
    try:
        new_review = await ReviewService.create_review(review)
        return await ReviewService.get_review(new_review.id, review.user_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при создании рецензии: {error}')
        raise


@router.put(
    '/{review_id}',
    response_model=ReviewResponse,
    summary='Обновление рецензии',
    response_description='Информация по обновленной рецензии',
    status_code=HTTPStatus.OK,
)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    user_id: UUID | None = None,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewResponse:
    """Обновление рецензии."""
    try:
        updated_review = await ReviewService.update_review(
            review_id,
            review_data,
        )
        return await ReviewService.get_review(updated_review.id, user_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при обновлении рецензии: {error}')
        raise


@router.get(
    '/{review_id}',
    response_model=ReviewResponse,
    summary='Получение рецензии',
    response_description='Информация по рецензии',
    status_code=HTTPStatus.OK,
)
async def get_review(
    review_id: UUID,
    user_id: UUID | None = None,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewResponse:
    """Получение рецензии по ID."""
    try:
        return await ReviewService.get_review(review_id, user_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при получении рецензии: {error}')
        raise


@router.get(
    '/filmwork/{filmwork_id}',
    response_model=list[ReviewResponse],
    summary='Получение рецензий кинопроизведения',
    response_description='Список рецензий',
    status_code=HTTPStatus.OK,
)
async def get_filmwork_reviews(
    filmwork_id: UUID,
    user_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query('created_at', regex='^(created_at|rating)$'),
    logger: logging.Logger = Depends(logging.getLogger),
) -> list[ReviewResponse]:
    """Получение рецензий для кинопроизведения с сортировкой."""
    try:
        return await ReviewService.get_filmwork_reviews(
            filmwork_id,
            user_id,
            skip,
            limit,
            sort_by,
        )
    except Exception as error:
        logger.error(f'Ошибка при получении рецензий: {error}')
        raise


@router.get(
    '/user/{user_id}',
    response_model=list[ReviewResponse],
    summary='Получение рецензий пользователя',
    response_description='Список рецензий пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_reviews(
    user_id: UUID,
    current_user_id: UUID | None = None,
    logger: logging.Logger = Depends(logging.getLogger),
) -> list[ReviewResponse]:
    """Получение всех рецензий пользователя."""
    try:
        return await ReviewService.get_user_reviews(user_id, current_user_id)
    except Exception as error:
        logger.error(f'Ошибка при получении рецензий пользователя: {error}')
        raise


@router.delete(
    '/{review_id}',
    response_model=ReviewResponse,
    summary='Удаление рецензии',
    response_description='Информация по удаленной рецензии',
    status_code=HTTPStatus.OK,
)
async def delete_review(
    review_id: UUID,
    user_id: UUID | None = None,
    logger: logging.Logger = Depends(logging.getLogger),
) -> ReviewResponse:
    """Удаление рецензии."""
    try:
        review = await ReviewService.get_review(review_id, user_id)
        await ReviewService.delete_review(review_id)
        return review
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при удалении рецензии: {error}')
        raise
