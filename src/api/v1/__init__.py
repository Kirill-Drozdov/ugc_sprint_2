"""Пакет с эндпоинтами приложения."""
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

# Для активации авторизации в Swagger UI.
auth_dep = AuthJWTBearer()
