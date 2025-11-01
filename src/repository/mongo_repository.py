from typing import Any, Generic, Type, TypeVar

from beanie import Document

from repository.abstract_repository import Repository

ModelType = TypeVar('ModelType', bound=Document)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=Document)


class MongoRepository(
    Repository,
    Generic[ModelType, UpdateSchemaType],
):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def delete(
        self,
        db_obj: ModelType,
    ):
        pass

    async def get_one(self, obj_id: Any) -> ModelType | None:
        return await self._model.find_one(self._model.id == obj_id)

    async def get_multi(self, *, skip=0, limit=100):
        pass

    async def create(self, *, obj_in: ModelType) -> ModelType:
        return await obj_in.insert()

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ):
        pass
