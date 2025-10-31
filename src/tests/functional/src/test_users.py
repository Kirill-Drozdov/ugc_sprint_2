from http import HTTPStatus
from typing import Callable
from uuid import UUID

import pytest

from tests.functional.conftest import BASE_API_V1_URL
from tests.functional.settings import test_settings

service_url = f'http://{test_settings.app_host}:{test_settings.app_port}'

_AUTH_API_URL = service_url + f'{BASE_API_V1_URL}/auth'
_SIGNUP_URL = f'{_AUTH_API_URL}/signup'
_HEADERS_JSON = {'Content-Type': 'application/json'}


@pytest.mark.asyncio
async def test_signup(make_post_request: Callable):
    """Проверка регистрации пользователя."""
    # Arrange.
    signup_data = {
        'login': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword123',
    }

    # Act.
    body, status = await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.CREATED
    assert body['login'] == 'testuser'
    assert body['first_name'] == 'Test'
    assert body['last_name'] == 'User'
    assert 'id' in body
    assert 'password' not in body
    # Проверяем что UUID валиден.
    UUID(body['id'])


@pytest.mark.asyncio
async def test_signup_existing_user(make_post_request: Callable):
    """Проверка регистрации существующего пользователя."""
    # Arrange.
    signup_data = {
        'login': 'existinguser',
        'first_name': 'Existing',
        'last_name': 'User',
        'password': 'password123',
    }

    # Создаем пользователя первый раз.
    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    # Act - пытаемся создать того же пользователя.
    body, status = await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.BAD_REQUEST
    assert 'detail' in body
    assert 'уже существует' in body['detail']


@pytest.mark.asyncio
async def test_login_success(make_post_request: Callable):
    """Проверка успешного входа в систему."""
    # Arrange - создаем пользователя.
    signup_data = {
        'login': 'loginuser',
        'first_name': 'Login',
        'last_name': 'User',
        'password': 'loginpass123',
    }

    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    login_data = {
        'login': 'loginuser',
        'password': 'loginpass123',
    }

    # Act.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.OK
    assert 'access' in body
    assert 'refresh' in body
    assert isinstance(body['access'], str)
    assert isinstance(body['refresh'], str)
    assert len(body['access']) > 0
    assert len(body['refresh']) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(make_post_request: Callable):
    """Проверка входа с неверным паролем."""
    # Arrange - создаем пользователя.
    signup_data = {
        'login': 'wrongpassuser',
        'first_name': 'Wrong',
        'last_name': 'Password',
        'password': 'correctpass',
    }

    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    login_data = {
        'login': 'wrongpassuser',
        'password': 'wrongpassword',
    }

    # Act.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.BAD_REQUEST
    assert 'detail' in body
    assert 'Неверно введены имя пользователя или пароль' in body['detail']


@pytest.mark.asyncio
async def test_login_nonexistent_user(make_post_request: Callable):
    """Проверка входа несуществующего пользователя."""
    # Arrange.
    login_data = {
        'login': 'nonexistent',
        'password': 'anypassword',
    }

    # Act.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.BAD_REQUEST
    assert 'detail' in body
    assert 'Неверно введены имя пользователя или пароль' in body['detail']


@pytest.mark.asyncio
async def test_refresh_token_success(make_post_request: Callable):
    """Проверка успешного обновления токена."""
    # Arrange - создаем пользователя и логинимся.
    signup_data = {
        'login': 'refreshuser',
        'first_name': 'Refresh',
        'last_name': 'User',
        'password': 'refreshpass123',
    }

    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    login_data = {
        'login': 'refreshuser',
        'password': 'refreshpass123',
    }

    login_body, _ = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    refresh_token = login_body['refresh']

    # Act - обновляем токен.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/refresh',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {refresh_token}',
        },
    )

    # Assert.
    assert status == HTTPStatus.OK
    assert 'access' in body
    assert 'refresh' in body
    assert isinstance(body['access'], str)
    assert isinstance(body['refresh'], str)
    # Новые токены должны отличаться от старых.
    assert body['access'] != login_body['access']
    assert body['refresh'] != login_body['refresh']


@pytest.mark.asyncio
async def test_refresh_token_invalid(make_post_request: Callable):
    """Проверка обновления токена с невалидным refresh токеном."""
    # Arrange.
    invalid_token = 'invalid.refresh.token'

    # Act.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/refresh',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {invalid_token}',
        },
    )

    # Assert.
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body
    assert 'Невалидный refresh-токен' in body['detail']


@pytest.mark.asyncio
async def test_logout_success(make_post_request: Callable):
    """Проверка успешного выхода из системы."""
    # Arrange - создаем пользователя и логинимся.
    signup_data = {
        'login': 'logoutuser',
        'first_name': 'Logout',
        'last_name': 'User',
        'password': 'logoutpass123',
    }

    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    login_data = {
        'login': 'logoutuser',
        'password': 'logoutpass123',
    }

    login_body, _ = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    access_token = login_body['access']

    # Act - выходим из системы.
    _, status = await make_post_request(
        url=f'{_AUTH_API_URL}/logout',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        },
    )

    # Assert.
    assert status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_logout_invalid_token(make_post_request: Callable):
    """Проверка выхода с невалидным токеном."""
    # Arrange.
    invalid_token = 'invalid.access.token'

    # Act.
    _, status = await make_post_request(
        url=f'{_AUTH_API_URL}/logout',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {invalid_token}',
        },
    )

    # Assert.
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout_without_token(make_post_request: Callable):
    """Проверка выхода без токена."""
    # Act.
    _, status = await make_post_request(
        url=f'{_AUTH_API_URL}/logout',
        query_data={},
        headers=_HEADERS_JSON,
    )

    # Assert.
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_after_logout(make_post_request: Callable):
    """Проверка невозможности обновления токена после выхода."""
    # Arrange - создаем пользователя, логинимся и выходим.
    signup_data = {
        'login': 'refreshlogoutuser',
        'first_name': 'RefreshLogout',
        'last_name': 'User',
        'password': 'password123',
    }

    await make_post_request(
        url=_SIGNUP_URL,
        query_data=signup_data,
        headers=_HEADERS_JSON,
    )

    login_data = {
        'login': 'refreshlogoutuser',
        'password': 'password123',
    }

    login_body, _ = await make_post_request(
        url=f'{_AUTH_API_URL}/login',
        query_data=login_data,
        headers=_HEADERS_JSON,
    )

    access_token = login_body['access']
    refresh_token = login_body['refresh']

    # Выходим из системы.
    await make_post_request(
        url=f'{_AUTH_API_URL}/logout',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        },
    )

    # Act - пытаемся обновить токен после выхода.
    body, status = await make_post_request(
        url=f'{_AUTH_API_URL}/refresh',
        query_data={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {refresh_token}',
        },
    )

    # Assert.
    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in body
    assert 'Невалидный refresh-токен' in body['detail']
