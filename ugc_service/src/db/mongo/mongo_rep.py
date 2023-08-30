from core.config import settings
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo import ReturnDocument
from pymongo.collection import DeleteResult, InsertOneResult, UpdateResult
from pymongo.errors import DuplicateKeyError


class MongoRepository:
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
            result: InsertOneResult = await collection.insert_one(document)
            logger.info(f'Added to {collection_name}: {document}')
            return str(result.inserted_id)
        except DuplicateKeyError as er:
            logger.exception(f'Error when adding an entry to the collection {collection_name}: {er}')
            raise er
        except Exception as er:
            logger.exception(f'Error when adding an entry to the collection {collection_name}: {er}')
            return None

    async def find_one(self, collection_name: str, query: dict[str, str]) -> dict[str, str] | None:
        """Поиск одной записи в коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            result: dict[str, str] = await collection.find_one(query)
            logger.info(f'One entrie in the {collection_name} found')
            return result
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the {collection_name}: {er}')
            return None

    async def find_all(
        self, collection_name: str, query: dict[str, str], page_size: int | None = None, page_number: int | None = None
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
            logger.info(f'Entries in the {collection_name} found')
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the {collection_name}: {er}')
            return []
        return await result.to_list(length=None)  # type: ignore[no-any-return]

    async def update_one(
        self, collection_name: str, query: dict[str, str], update_data: dict[str, str]
    ) -> dict[str, str] | None:
        """Обновление одной записи в коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            result: UpdateResult = await collection.find_one_and_update(
                query, {'$set': update_data}, return_document=ReturnDocument.AFTER
            )
            if result.modified_count > 0:
                logger.info(f'Entry in {collection_name} updated successfully')
                return result  # type: ignore[no-any-return]
            else:
                logger.warning('No entry matched the given query')
                return None
        except Exception as er:
            logger.exception(f'Error updating a entry in the {collection_name}: {er}')
            return None

    async def delete_one(self, collection_name: str, query: dict[str, str]) -> int | None:
        """Удаление одной записи из коллекции по запросу."""
        try:
            database = await self.get_database()
            collection = database[collection_name]
            result: DeleteResult = await collection.delete_one(query)
            logger.info(f'One entry was deleted from the {collection_name}')
        except Exception as er:
            logger.exception(f'Error when deleting an entry from a {collection_name}: {er}')
            return None
        return result.deleted_count  # type: ignore[no-any-return]


mongo_repository: MongoRepository | None = None


def get_mongo_repository() -> MongoRepository | None:
    return mongo_repository
