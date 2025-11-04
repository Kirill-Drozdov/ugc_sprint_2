from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from db.models import Bookmark
from schemas.bookmark import BookmarkCreate, BookmarkResponse
from services.bookmark import BookmarkService

router = APIRouter()


@router.post(
    '/',
    response_model=BookmarkResponse,
    summary='Создание закладки',
    response_description='Информация по закладке',
    status_code=HTTPStatus.CREATED,
)
async def create_new_bookmark(
    bookmark: BookmarkCreate,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Bookmark:
    """Создание закладки.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    """
    try:
        return await BookmarkService.create_bookmark(bookmark)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(
            f'Ошибка при создании закладки: {error}',
        )
        raise


@router.get(
    '/{user_id}',
    response_model=list[Bookmark],
    summary='Просмотр закладки пользователя',
    response_description='Информация по закладке пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_bookmarks(
    user_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> list[Bookmark]:
    """Просмотр закладок пользователя.

    - **_id**: идентификатор закладки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **created_at**: время создания закладки.
    """
    try:
        return await BookmarkService.get_user_bookmarks(user_id)
    except Exception as error:
        logger.error(
            f'Ошибка при просмотре закладок пользователя: {error}',
        )
        raise


@router.delete(
    '/{bookmark_id}',
    response_model=Bookmark,
    summary='Удаление закладки пользователя',
    response_description='Информация по удаленной закладке пользователя',
    status_code=HTTPStatus.OK,
)
async def delete_bookmark(
    bookmark_id: UUID,
    logger: logging.Logger = Depends(logging.getLogger),
) -> Bookmark:
    """Удаление закладки пользователя.

    - **_id**: идентификатор закладки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **created_at**: время создания закладки.
    """
    try:
        return await BookmarkService.delete_bookmark(bookmark_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.error(
            f'Ошибка при удалении закладки: {error}',
        )
        raise
