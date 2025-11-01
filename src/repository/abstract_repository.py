from abc import ABC, abstractmethod


class Repository(ABC):
    """Абстрактный класс для взаимодействия с хранилищем данных.
    """

    @abstractmethod
    async def delete(self, *args, **kwargs):
        ...

    @abstractmethod
    async def update(self, *args, **kwargs):
        ...

    @abstractmethod
    async def create(self, *args, **kwargs):
        ...

    @abstractmethod
    async def get_one(self, *args, **kwargs):
        ...

    @abstractmethod
    async def get_multy(self, *args, **kwargs):
        ...
