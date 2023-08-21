import time

import psycopg2  # type: ignore
from fake_data import create_bookmarks, create_film_ratings, create_reviews
from pydantic import BaseModel  # type: ignore


class PostgresConfig(BaseModel):
    PG_HOST: str = "localhost"
    PG_PORT: int = 5433
    PG_DATABASE: str = "test_database"
    PG_USER: str = "app"
    PG_PASSWORD: str = "123qwe"

    class Config:
        env_file = ".env"
        env_prefix = "POSTGRES_"


USER_FILM_RATINGS_TABLE = "ratings"
REVIEWS_TABLE = "reviews"
BOOKMARKS_TABLE = "bookmarks"


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time:.6f} seconds")
        return result

    return wrapper


def create_tables(conn):
    cursor = conn.cursor()

    create_user_film_ratings_table = """
    CREATE TABLE IF NOT EXISTS user_film_ratings (
        id SERIAL PRIMARY KEY,
        user_id UUID NOT NULL,
        film_id UUID NOT NULL,
        rating SMALLINT NOT NULL,
        date_created TIMESTAMP NOT NULL
    )
    """

    create_reviews_table = """
    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        user_id UUID NOT NULL,
        film_id UUID NOT NULL,
        text TEXT NOT NULL,
        date_created TIMESTAMP NOT NULL
    )
    """

    create_bookmarks_table = """
    CREATE TABLE IF NOT EXISTS bookmarks (
        id SERIAL PRIMARY KEY,
        user_id UUID NOT NULL,
        film_id UUID NOT NULL,
        date_created TIMESTAMP NOT NULL
    )
    """

    cursor.execute(create_user_film_ratings_table)
    cursor.execute(create_reviews_table)
    cursor.execute(create_bookmarks_table)

    conn.commit()
    cursor.close()


def insert_data_into_table(conn, table_name, data: list[dict]):
    cursor = conn.cursor()

    columns = ", ".join(data[0].keys())
    placeholders = ", ".join(["%s"] * len(data[0]))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    values = [tuple(item.values()) for item in data]

    cursor.executemany(query, values)
    conn.commit()

    cursor.close()


def measure_write_speed(conn, table_name, data):
    create_tables(conn)

    cursor = conn.cursor()

    @measure_execution_time
    def insert_data():
        columns = ", ".join(data[0].keys())
        placeholders = ", ".join(["%s"] * len(data[0]))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = [tuple(item.values()) for item in data]
        cursor.executemany(query, values)
        conn.commit()

    insert_data()
    cursor.close()


def measure_likes_count(conn, film_id):
    cursor = conn.cursor()

    @measure_execution_time
    def count_likes():
        query = f"""
            SELECT film_id, COUNT(*) as likes_count
            FROM {USER_FILM_RATINGS_TABLE}
            WHERE film_id = %s
            GROUP BY film_id
        """
        cursor.execute(query, (film_id,))
        result = cursor.fetchall()
        return result

    likes_count_result = count_likes()
    cursor.close()
    return likes_count_result


def measure_average_rating(conn, film_id):
    cursor = conn.cursor()

    @measure_execution_time
    def calculate_average_rating():
        query = f"""
            SELECT AVG(rating) as average_rating
            FROM {USER_FILM_RATINGS_TABLE}
            WHERE film_id = %s
        """
        cursor.execute(query, (film_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    average_rating = calculate_average_rating()
    cursor.close()
    return average_rating


def view_bookmarks_for_user(conn, user_id):
    cursor = conn.cursor()

    @measure_execution_time
    def get_user_bookmarks():
        query = f"""
            SELECT * FROM {BOOKMARKS_TABLE}
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        return result

    user_bookmarks = get_user_bookmarks()
    cursor.close()
    return user_bookmarks


def main():
    num_elements = 100

    global config
    config = PostgresConfig()

    conn = psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DATABASE,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
    )

    user_film_ratings = list(create_film_ratings(num_elements))
    reviews = list(create_reviews(num_elements))
    bookmarks = list(create_bookmarks(num_elements))

    user_film_ratings_dicts = [item.__dict__ for item in user_film_ratings]
    reviews_dicts = [item.__dict__ for item in reviews]
    bookmarks_dicts = [item.__dict__ for item in bookmarks]

    measure_write_speed(conn, USER_FILM_RATINGS_TABLE, user_film_ratings_dicts)
    measure_write_speed(conn, REVIEWS_TABLE, reviews_dicts)
    measure_write_speed(conn, BOOKMARKS_TABLE, bookmarks_dicts)

    film_id = user_film_ratings[0].film_id
    likes_count_result = measure_likes_count(conn, film_id)
    print("Likes count for each movie:")
    print(likes_count_result)

    film_id = user_film_ratings[0].film_id
    average_rating = measure_average_rating(conn, film_id)
    print(f"Average rating for film with film_id '{film_id}': {average_rating:.2f}")

    user_id = bookmarks[0].user_id
    user_bookmarks = view_bookmarks_for_user(conn, user_id)
    print(f"Bookmarks for user with user_id '{user_id}':")
    print(user_bookmarks)

    conn.close()


if __name__ == "__main__":
    main()
