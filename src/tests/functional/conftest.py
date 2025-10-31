"""Модуль с фикстурами тестов."""
import asyncio
from typing import Callable

import aiohttp
import pytest

BASE_API_V1_URL: str = '/api/v1'


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name='aiohttp_session', scope='session')
async def aiohttp_session():
    """Фикстура для предоставления клиентской сессии."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(name='make_get_request')
def make_get_request(aiohttp_session: aiohttp.ClientSession) -> Callable:
    """Фикстура для выполнения запроса к API."""
    async def inner(url: str, query_data: dict[str, str], headers: dict):
        async with aiohttp_session.get(
            url,
            params=query_data,
            headers=headers,
        ) as response:
            body = await response.json()
            status = response.status
            return body, status
    return inner


@pytest.fixture(name='make_post_request')
def make_post_request(aiohttp_session: aiohttp.ClientSession) -> Callable:
    """Фикстура для выполнения POST запроса к API."""
    async def inner(url: str, query_data: dict, headers: dict):
        async with aiohttp_session.post(
            url,
            json=query_data,
            headers=headers,
        ) as response:
            body = await response.json()
            status = response.status
            return body, status
    return inner
