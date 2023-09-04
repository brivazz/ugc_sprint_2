"""Файл создания подключения/отключения к MongoDB и создание коллекций."""

from core.config import settings
from db.mongo import mongo_rep  # type: ignore[attr-defined]
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB client
mongo_client: AsyncIOMotorClient | None = None


async def on_startup(data_storage_hosts: list[str]) -> None:
    """Выполняет необходимые операции при запуске приложения."""
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(
            data_storage_hosts,  # , username=settings.mongo_username, password=settings.mongo_password
        )
        db = mongo_client[settings.mongo_db]

        if 'film_bookmarks' not in await db.list_collection_names():
            collection = db['film_bookmarks']
            collection.create_index([('film_id', 1), ('user_id', 1)], unique=True)
        if 'film_scores' not in await db.list_collection_names():
            collection = db['film_score']
            collection.create_index([('film_id', 1), ('user_id', 1)], unique=True)
        if 'film_reviews' not in await db.list_collection_names():
            collection = db['film_reviews']
            collection.create_index([('film_id', 1), ('user_id', 1)], unique=True)

        mongo_rep.mongo_repository = mongo_rep.MongoRepository(mongo_client)
        logger.info('Connected to MongoDB successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')


def on_shutdown() -> None:
    """
    Выполняет необходимые операции при завершении работы приложения.

    Закрывает соединение с MongoDB, если оно было установлено.
    """
    if mongo_client:
        mongo_client.close()
        logger.info('Disconnected from MongoDB.')
