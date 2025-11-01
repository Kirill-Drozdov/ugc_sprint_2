import contextlib

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api.v1 import bookmark, rating, review, review_like
from core.config import settings
from db.models import Review


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    client = AsyncIOMotorClient(
        f'{settings.mongo_host}:{settings.mongo_port}',
    )
    await init_beanie(
        database=client.ugc,  # type: ignore
        document_models=[
            bookmark.Bookmark,
            rating.Rating,
            Review,
            review_like.ReviewLike,
        ],
    )
    yield
    client.close()


def get_app() -> FastAPI:  # noqa CFQ004
    """Производит инициализацию приложения.

    Returns:
        Объект приложения FastAPI.
    """

    app = FastAPI(
        title=settings.project_name,
        docs_url='/openapi',
        openapi_url='/openapi.json',
        default_response_class=ORJSONResponse,
        lifespan=lifespan,  # type: ignore
    )

    # Подключение роутеров.
    app.include_router(
        bookmark.router,
        prefix='/api/v1/bookmarks',
        tags=['Bookmark'],
    )
    app.include_router(
        rating.router,
        prefix='/api/v1/ratings',
        tags=['Rating'],
    )
    app.include_router(
        review.router,
        prefix='/api/v1/reviews',
        tags=['Review'],
    )
    app.include_router(
        review_like.router,
        prefix='/api/v1/review-likes',
        tags=['Review Like'],
    )

    return app


app = get_app()
