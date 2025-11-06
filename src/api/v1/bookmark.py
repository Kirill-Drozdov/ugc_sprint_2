from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter

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
) -> Bookmark:
    """Создание закладки.

    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    """
    return await BookmarkService.create_bookmark(bookmark)


@router.get(
    '/{user_id}',
    response_model=list[Bookmark],
    summary='Просмотр закладки пользователя',
    response_description='Информация по закладке пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_bookmarks(
    user_id: UUID,
) -> list[Bookmark]:
    """Просмотр закладок пользователя.

    - **_id**: идентификатор закладки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **created_at**: время создания закладки.
    """
    return await BookmarkService.get_user_bookmarks(user_id)


@router.delete(
    '/{bookmark_id}',
    response_model=Bookmark,
    summary='Удаление закладки пользователя',
    response_description='Информация по удаленной закладке пользователя',
    status_code=HTTPStatus.OK,
)
async def delete_bookmark(
    bookmark_id: UUID,
) -> Bookmark:
    """Удаление закладки пользователя.

    - **_id**: идентификатор закладки.
    - **filmwork_id**: идентификатор кинопроизведения.
    - **user_id**: идентификатор пользователя.
    - **created_at**: время создания закладки.
    """
    return await BookmarkService.delete_bookmark(bookmark_id)
