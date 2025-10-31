from pydantic import Field
from beanie import Document, Indexed
from uuid import UUID, uuid4
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


class Post(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    subject: Indexed(str, unique=False)  # type: ignore
    text: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


@router.post(
    '/',
    response_model=Post,
    summary='Создание записи',
    response_description='Информация по записи',
    status_code=HTTPStatus.OK,
)
async def create_new_post(
    post: Post,
) -> Post:
    """Создание записи.

    - **subject**: .
    - **text**: .
    """
    post = await Post(subject=post.subject, text=post.text).insert()
    return post


@router.get(
    '/',
    response_model=list[Post],
    summary='Создание записи',
    response_description='Информация по записи',
    status_code=HTTPStatus.OK,
)
async def get_posts() -> list[Post]:
    """Создание записи.

    - **subject**: .
    - **text**: .
    """
    post = await Post.find_all().to_list()
    return post
