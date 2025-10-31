import contextlib

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.v1 import post
from core.config import settings


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    client = AsyncIOMotorClient('localhost:27019')
    await init_beanie(
        database=client.ugc,  # type: ignore
        document_models=[post.Post],
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
    app.include_router(post.router, prefix='/api/v1/posts', tags=['Post'])

    return app


app = get_app()
