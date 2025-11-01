from http import HTTPStatus
import logging
from uuid import UUID

from fastapi import HTTPException

from schemas.bookmark import Bookmark, BookmarkCreate


class BookmarkService:
    logger = logging.getLogger(__name__)

    @classmethod
    async def delete_bookmark(
        cls,
        bookmark_id: UUID,
    ) -> Bookmark:
        """Удаляет закладку, если она существует."""
        bookmark = await Bookmark.find_one(
            Bookmark.id == bookmark_id,
        )
        if bookmark is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Это кинопроизведение уже добавлено в закладки.',
            )
        await bookmark.delete()
        return bookmark

    @classmethod
    async def create_bookmark(
        cls,
        bookmark_data: BookmarkCreate,
    ) -> Bookmark:
        """Создает закладку, если она не существует."""

        # Проверяем существование закладки.
        existing = await Bookmark.find_one(
            Bookmark.user_id == bookmark_data.user_id,
            Bookmark.filmwork_id == bookmark_data.filmwork_id,
        )

        if existing:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Это кинопроизведение уже добавлено в закладки.',
            )
        bookmark = Bookmark(
            user_id=bookmark_data.user_id,
            filmwork_id=bookmark_data.filmwork_id,
        )
        return await bookmark.insert()

    @classmethod
    async def get_user_bookmarks(cls, user_id: UUID) -> list[Bookmark]:
        """Возвращает все закладки пользователя."""
        return await Bookmark.find(
            Bookmark.user_id == user_id,
        ).sort(-Bookmark.created_at).to_list()  # type: ignore
