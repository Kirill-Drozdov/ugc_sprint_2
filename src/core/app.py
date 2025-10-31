import contextlib

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse

from api.v1 import role, user
from core.config import settings
from db import redis


# @contextlib.asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Асинхронный контекстный менеджер для управления событиями запуска
#         и завершения работы приложения.

#     Args:
#         app: Экземпляр приложения FastAPI.
#     """
#     # STARTUP: Подключаемся к базам данных.
#     redis.redis = Redis(
#         host=settings.redis_host,
#         port=settings.redis_port,
#         db=0,
#         decode_responses=True,
#     )
#     # Передаем управление приложению.
#     yield
#     # SHUTDOWN: Корректно закрываем соединения.
#     if redis.redis is not None:
#         await redis.redis.close()


def get_app() -> FastAPI:  # noqa CFQ004
    """Производит инициализацию приложения.

    Returns:
        Объект приложения FastAPI.
    """

    app = FastAPI(
        title=settings.project_name,
        root_path='/api/auth',
        docs_url='/openapi',
        openapi_url='/openapi.json',
        default_response_class=ORJSONResponse,
        # lifespan=lifespan,
    )

    # Подключение роутеров.
    # app.include_router(user.router, prefix='/api/v1/auth', tags=['Auth'])

    return app


app = get_app()
