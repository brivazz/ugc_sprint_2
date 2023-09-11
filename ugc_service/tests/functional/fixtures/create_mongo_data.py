import contextlib

import motor.motor_asyncio
import pytest
from functional.settings import settings_test
from pymongo.errors import OperationFailure

COLLECTION_NAMES = [
    'film_bookmarks',
    'film_score',
    'film_reviews',
]


@pytest.fixture(scope='session')
async def mongo_client():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        [f'{settings_test.mongo_host}:{settings_test.mongo_port}'],
        # username=settings_test.mongo_username,
        # password=settings_test.mongo_password,
    )
    yield client
    await client.close()


@pytest.fixture(scope='session', autouse=True)
async def delete_all_mongo_data(mongo_client: motor.motor_asyncio.AsyncIOMotorClient):
    async def delete_data(client):
        db = client[settings_test.mongo_db]

        for collection_name in COLLECTION_NAMES:
            with contextlib.suppress(OperationFailure):
                collection = db[collection_name]
                await collection.delete_many({})

    await delete_data(mongo_client)
    yield
    await delete_data(mongo_client)
