import pymongo
from pydantic import BaseConfig

from fake_data import create_user_film_ratings, create_reviews, create_bookmarks


class MongoDBConfig(BaseConfig):
    MONGO_CONNECTION_STRING: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "someDb"

    class Config:
        env_file = ".env"
        env_prefix = "MONGODB_"

BATCH_SIZE = 10_000
USER_FILM_RATINGS_COLLECTION = "user_film_ratings"
REVIEWS_COLLECTION = "reviews"
BOOKMARKS_COLLECTION = "bookmarks"

def create_batch(iterable, n=1):
    batch = []
    for elem in iterable:
        batch.append(elem)
        if len(batch) % n == 0:
            yield batch
            batch = []
    if batch:
        yield batch

def create_collections():
    client = pymongo.MongoClient(config.MONGO_CONNECTION_STRING)
    database = client[config.DATABASE_NAME]

    if USER_FILM_RATINGS_COLLECTION not in database.list_collection_names():
        database.create_collection(USER_FILM_RATINGS_COLLECTION)
        # client.admin.command('enableSharding', config.DATABASE_NAME)
        client.admin.command('shardCollection', f"{config.DATABASE_NAME}.{USER_FILM_RATINGS_COLLECTION}", key={'_id': 'hashed'})
        database[USER_FILM_RATINGS_COLLECTION].create_index([("film_id", pymongo.ASCENDING)])

    if REVIEWS_COLLECTION not in database.list_collection_names():
        database.create_collection(REVIEWS_COLLECTION)
        # client.admin.command('enableSharding', config.DATABASE_NAME)
        client.admin.command('shardCollection', f"{config.DATABASE_NAME}.{USER_FILM_RATINGS_COLLECTION}", key={'_id': 'hashed'})
        database[REVIEWS_COLLECTION].create_index([("film_id", pymongo.ASCENDING)])

    if BOOKMARKS_COLLECTION not in database.list_collection_names():
        database.create_collection(BOOKMARKS_COLLECTION)
        # client.admin.command('enableSharding', config.DATABASE_NAME)
        client.admin.command('shardCollection', f"{config.DATABASE_NAME}.{USER_FILM_RATINGS_COLLECTION}", key={'_id': 'hashed'})
        database[BOOKMARKS_COLLECTION].create_index([("user_id", pymongo.ASCENDING)])


def insert_data_into_collection(collection_name, data: list[dict]):
    client = pymongo.MongoClient(config.MONGO_CONNECTION_STRING)
    database = client[config.DATABASE_NAME]
    collection = database[collection_name]
    collection.insert_many(data)


def get_collection_counts():
    client = pymongo.MongoClient(config.MONGO_CONNECTION_STRING)
    database = client[config.DATABASE_NAME]

    user_film_ratings_count = database[USER_FILM_RATINGS_COLLECTION].count_documents({})
    reviews_count = database[REVIEWS_COLLECTION].count_documents({})
    bookmarks_count = database[BOOKMARKS_COLLECTION].count_documents({})

    return user_film_ratings_count, reviews_count, bookmarks_count


def user_film_insert(num):
    user_film_ratings = create_user_film_ratings(num)
    for counter, batch in enumerate(create_batch(user_film_ratings, BATCH_SIZE), start=1):
        insert_data_into_collection(USER_FILM_RATINGS_COLLECTION, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def reviews_insert(num):
    reviews = create_reviews(num)
    for counter, batch in enumerate(create_batch(reviews, BATCH_SIZE), start=1):
        insert_data_into_collection(REVIEWS_COLLECTION, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def bookmarks_insert(num):
    bookmarks = create_bookmarks(num)
    for counter, batch in enumerate(create_batch(bookmarks, BATCH_SIZE), start=1):
        insert_data_into_collection(BOOKMARKS_COLLECTION, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def main():
    num_elements = 15 * 1_000_000

    global config
    config = MongoDBConfig()

    create_collections()

    user_film_insert(num_elements)
    reviews_insert(num_elements)
    bookmarks_insert(num_elements)

    print(f"{20 * '='}\nData insertion completed successfully!")

    user_film_ratings_count, reviews_count, bookmarks_count = get_collection_counts()
    print(
        f"Collection '{USER_FILM_RATINGS_COLLECTION}' count: {user_film_ratings_count}"
    )
    print(f"Collection '{REVIEWS_COLLECTION}' count: {reviews_count}")
    print(f"Collection '{BOOKMARKS_COLLECTION}' count: {bookmarks_count}")


if __name__ == "__main__":
    main()
