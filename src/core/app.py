import contextlib
from http import HTTPStatus
import logging

from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
import logstash
from motor.motor_asyncio import AsyncIOMotorClient
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from api.v1 import bookmark, rating, review, review_like
from core.config import settings
from db import models


def init_sentry():
    """Инициализация Sentry."""
    if not settings.sentry_dsn:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
    )


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):

    init_sentry()

    client: AsyncIOMotorClient = AsyncIOMotorClient(
        f'{settings.mongo_host}:{settings.mongo_port}',
    )
    await init_beanie(
        database=client.ugc,  # type: ignore
        document_models=[
            models.Bookmark,
            models.Rating,
            models.Review,
            models.ReviewLike,
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
        root_path='/api/ugc',
        docs_url='/openapi',
        openapi_url='/openapi.json',
        default_response_class=ORJSONResponse,
        lifespan=lifespan,  # type: ignore
    )

    logging.getLogger('').addHandler(
        logstash.LogstashHandler(
            settings.logstash_host,
            settings.logstash_port,
            version=1,
        ),
    )
    logging.getLogger('').setLevel(logging.INFO)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):  # noqa
        """Глобальный обработчик исключений."""
        sentry_sdk.capture_exception(exc)
        return ORJSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={'detail': 'Internal server error'},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(  # noqa
        request: Request,
        exc: RequestValidationError,
    ):
        """Обработчик ошибок валидации."""
        sentry_sdk.capture_exception(exc)
        return ORJSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={'detail': exc.errors()},
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
