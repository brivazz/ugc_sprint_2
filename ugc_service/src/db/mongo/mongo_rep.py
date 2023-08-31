"""Репозиторий для взаимодействия с MongoDB."""

from core.config import settings
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo import ReturnDocument
from pymongo.collection import InsertOneResult, UpdateResult


class MongoRepository:
    """Класс для взаимодействия с коллекциями MongoDB."""

    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        """Инициализирует экземпляр класса MongoRepository."""
        self._mongo_client: AsyncIOMotorClient = db_client

    async def get_database(self) -> AsyncIOMotorClient:
        """Получает объект базы данных."""
        return self._mongo_client[settings.mongo_db]

    async def insert_one(self, collection_name: str, document: dict[str, str]) -> str | None:
        """Добавление одной записи в коллекцию."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            if await self.find_one(collection_name, document):
                logger.exception(f'Entry for user: {document["user_id"]} in the {collection_name}: already exists')
                return None
            insert_one_result: InsertOneResult = await collection.insert_one(document)
            logger.info(f'User: {document["user_id"]} added an entry to the collection: {collection_name}')
            return str(insert_one_result.inserted_id)
        except Exception as er:
            logger.exception(f'Error when adding an entry to the collection {collection_name}: {er}')
            return None

    async def find_one(self, collection_name: str, query: dict[str, str]) -> dict[str, str] | None:
        """Поиск одной записи в коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            if find_one_result := await collection.find_one(query):
                return find_one_result  # type: ignore[no-any-return]
            return None
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the {collection_name}: {er}')
            return None

    async def find_all(
        self,
        collection_name: str,
        query: dict[str, str],
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> list[dict[str, str]] | None:
        """Поиск всех записей в коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]

            if page_size and page_number:
                skip_count = (page_number - 1) * page_size
                result: AsyncIOMotorCursor = collection.find(query).skip(skip_count).limit(page_size)
            else:
                result = collection.find(query)
            entries = await result.to_list(length=None)
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the collection: {collection_name}: {er}')
            return None
        if entries:
            logger.info(
                f'Entries for User: {query["user_id"]} in the collection: {collection_name} found {len(entries)}',
            )
            return entries  # type: ignore[no-any-return]
        logger.info(f'Entries for user: {query["user_id"]} in the collection: {collection_name} not found')
        return None  # type: ignore[no-any-return]

    async def update_one(
        self,
        collection_name: str,
        query: dict[str, str],
        update_data: dict[str, str],
    ) -> dict[str, str] | None:
        """Обновление одной записи в коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            update_result: UpdateResult = await collection.find_one_and_update(
                query,
                {'$set': update_data},
                return_document=ReturnDocument.AFTER,
            )
            if update_result.modified_count > 0:
                logger.info(f'Entry in the collection: {collection_name} updated successfully')
                return update_result  # type: ignore[no-any-return]

            logger.warning('No entry matched the given query')
            return None
        except Exception as er:
            logger.exception(f'Error updating a entry in the collection: {collection_name}: {er}')
            return None

    async def delete_one(self, collection_name: str, query: dict[str, str]) -> int | None:
        """Удаление одной записи из коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            if await self.find_one(collection_name, query):
                delete_result = await collection.delete_one(query)
                logger.info(f'User: {query["user_id"]} an entry was deleted from the collection: {collection_name}')
                return delete_result.deleted_count  # type: ignore[no-any-return]
            logger.info(f'Entry for User: {query["user_id"]} in the collection: {collection_name} not found')
            return None
        except Exception as er:
            logger.exception(f'Error when deleting an entry from a collection: {collection_name}: {er}')
            return None


mongo_repository: MongoRepository | None = None


def get_mongo_repository() -> MongoRepository | None:
    """Возвращает объект MongoRepository или None."""
    return mongo_repository
