import time

import pymongo

from config import mongo_cfg
from fake_data import create_film_ratings, create_reviews, create_bookmarks



def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time:.6f} seconds")
        return result

    return wrapper


def measure_write_speed(collection_name, data):
    client = pymongo.MongoClient(mongo_cfg.mongo_connection_string)
    database = client[mongo_cfg.db_name]
    collection = database[collection_name]

    @measure_execution_time
    def insert_data():
        collection.insert_many(data)

    insert_data()


def measure_likes_count():
    client = pymongo.MongoClient(mongo_cfg.mongo_connection_string)
    database = client[mongo_cfg.db_name]
    collection = database[mongo_cfg.film_ratings_collection]

    @measure_execution_time
    def count_likes():
        pipeline = [{"$group": {"_id": "$film_id", "likes_count": {"$sum": 1}}}]
        result = collection.aggregate(pipeline)
        return list(result)

    return count_likes()


def measure_average_rating(film_id):
    client = pymongo.MongoClient(mongo_cfg.mongo_connection_string)
    database = client[mongo_cfg.db_name]
    collection = database[mongo_cfg.film_ratings_collection]

    @measure_execution_time
    def calculate_average_rating():
        pipeline = [
            {"$match": {"film_id": film_id}},
            {"$group": {"_id": None, "average_rating": {"$avg": "$rating"}}},
        ]
        result = list(collection.aggregate(pipeline))
        return result[0]["average_rating"] if result else 0

    return calculate_average_rating()


def view_bookmarks_for_user(user_id):
    client = pymongo.MongoClient(mongo_cfg.mongo_connection_string)
    database = client[mongo_cfg.db_name]
    collection = database[mongo_cfg.bookmarks_collection]

    @measure_execution_time
    def get_user_bookmarks():
        return list(collection.find({"user_id": user_id}))

    return get_user_bookmarks()


def main():
    num_elements = 10

    user_film_ratings = list(create_film_ratings(num_elements))
    reviews = list(create_reviews(num_elements))
    bookmarks = list(create_bookmarks(num_elements))

    user_film_ratings_dicts = [item.__dict__ for item in user_film_ratings]
    reviews_dicts = [item.__dict__ for item in reviews]
    bookmarks_dicts = [item.__dict__ for item in bookmarks]

    measure_write_speed(mongo_cfg.film_ratings_collection, user_film_ratings_dicts)
    measure_write_speed(mongo_cfg.reviews_collection, reviews_dicts)
    measure_write_speed(mongo_cfg.bookmarks_collection, bookmarks_dicts)

    likes_count_result = measure_likes_count()
    print("Likes count for each movie:")
    print(likes_count_result)

    film_id = user_film_ratings[0].film_id
    average_rating = measure_average_rating(film_id)
    print(f"Average rating for film with film_id '{film_id}': {average_rating:.2f}")

    user_id = bookmarks[0].user_id
    user_bookmarks = view_bookmarks_for_user(user_id)
    print(f"Bookmarks for user with user_id '{user_id}':")
    print(user_bookmarks)


if __name__ == "__main__":
    main()
