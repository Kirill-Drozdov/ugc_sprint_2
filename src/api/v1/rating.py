from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from schemas.rating import (
    FilmworkRatingSummary,
    Rating,
    RatingCreate,
    RatingResponse,
    RatingUpdate,
)
from services.rating import RatingService

router = APIRouter()


@router.post(
    '/',
    response_model=RatingResponse,
    summary='Создание оценки',
    response_description='Информация по оценке',
    status_code=HTTPStatus.CREATED,
)
async def create_rating(
    rating: RatingCreate,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Rating:
    """Создание новой оценки кинопроизведения.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    try:
        return await RatingService.create_rating(rating)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при создании оценки: {error}')
        raise


@router.put(
    '/{user_id}/{rating_id}',
    response_model=RatingResponse,
    summary='Обновление оценки',
    response_description='Информация по обновленной оценке',
    status_code=HTTPStatus.OK,
)
async def update_rating(
    user_id: UUID,
    rating_id: UUID,
    rating_data: RatingUpdate,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Rating:
    """Обновление существующей оценки.

    - **rating**: новая оценка от 0 до 10.
    """
    try:
        return await RatingService.update_rating(
            user_id,
            rating_id,
            rating_data,
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при обновлении оценки: {error}')
        raise


@router.get(
    '/user/{user_id}/filmwork/{filmwork_id}',
    response_model=RatingResponse,
    summary='Получение оценки пользователя',
    response_description='Информация по оценке',
    status_code=HTTPStatus.OK,
)
async def get_user_filmwork_rating(
    user_id: UUID,
    filmwork_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Rating:
    """Получение оценки пользователя для кинопроизведения.

    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    try:
        rating = await RatingService.get_user_rating(user_id, filmwork_id)
        if rating is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Оценка не найдена',
            )
        return rating
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при получении оценки: {error}')
        raise


@router.get(
    '/filmwork/{filmwork_id}/summary',
    response_model=FilmworkRatingSummary,
    summary='Сводная информация по рейтингам',
    response_description='Сводная информация по рейтингам кинопроизведения',
    status_code=HTTPStatus.OK,
)
async def get_filmwork_rating_summary(
    filmwork_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> FilmworkRatingSummary:
    """Получение сводной информации по рейтингам кинопроизведения.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **average_rating**: средний рейтинг.
    - **likes_count**: число лайков.
    - **dislikes_count**: число дизлайков.
    - **ratings_count**: суммарное число оценок.
    """
    try:
        return await RatingService.get_filmwork_rating_summary(filmwork_id)
    except Exception as error:
        logger.error(f'Ошибка при получении сводной информации: {error}')
        raise


@router.get(
    '/user/{user_id}',
    response_model=list[RatingResponse],
    summary='Получение всех оценок пользователя',
    response_description='Список оценок пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_ratings(
    user_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> list[Rating]:
    """Получение всех оценок пользователя.
    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    try:
        return await RatingService.get_user_ratings(user_id)
    except Exception as error:
        logger.error(f'Ошибка при получении оценок пользователя: {error}')
        raise


@router.delete(
    '/user/{user_id}/filmwork/{filmwork_id}',
    response_model=RatingResponse,
    summary='Удаление оценки',
    response_description='Информация по удаленной оценке',
    status_code=HTTPStatus.OK,
)
async def delete_rating(
    user_id: UUID,
    filmwork_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Rating:
    """Удаление оценки пользователя для кинопроизведения.
    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    try:
        rating = await RatingService.delete_rating(user_id, filmwork_id)
        if rating is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Оценка не найдена',
            )
        return rating
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Ошибка при удалении оценки: {error}')
        raise
