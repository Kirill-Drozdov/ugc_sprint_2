from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter

from db.models import Rating
from schemas.rating import (
    FilmworkRatingSummary,
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
) -> Rating:
    """Создание новой оценки кинопроизведения.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    return await RatingService.create_rating(rating)


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
) -> Rating:
    """Обновление существующей оценки.

    - **rating**: новая оценка от 0 до 10.
    """
    return await RatingService.update_rating(
        user_id,
        rating_id,
        rating_data,
    )


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
) -> Rating:
    """Получение оценки пользователя для кинопроизведения.

    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    return await RatingService.get_user_rating(user_id, filmwork_id)


@router.get(
    '/filmwork/{filmwork_id}/summary',
    response_model=FilmworkRatingSummary,
    summary='Сводная информация по рейтингам',
    response_description='Сводная информация по рейтингам кинопроизведения',
    status_code=HTTPStatus.OK,
)
async def get_filmwork_rating_summary(
    filmwork_id: UUID,
) -> FilmworkRatingSummary:
    """Получение сводной информации по рейтингам кинопроизведения.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **average_rating**: средний рейтинг.
    - **likes_count**: число лайков.
    - **dislikes_count**: число дизлайков.
    - **ratings_count**: суммарное число оценок.
    """
    return await RatingService.get_filmwork_rating_summary(filmwork_id)


@router.get(
    '/user/{user_id}',
    response_model=list[RatingResponse],
    summary='Получение всех оценок пользователя',
    response_description='Список оценок пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_ratings(
    user_id: UUID,
) -> list[Rating]:
    """Получение всех оценок пользователя.
    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    return await RatingService.get_user_ratings(user_id)


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
) -> Rating:
    """Удаление оценки пользователя для кинопроизведения.
    - **id**: идентификатор оценки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **rating**: оценка от 0 до 10.
    """
    return await RatingService.delete_rating(user_id, filmwork_id)
