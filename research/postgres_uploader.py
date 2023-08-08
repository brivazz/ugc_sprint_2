import psycopg2
from pydantic import BaseConfig

from fake_data import create_user_film_ratings, create_reviews, create_bookmarks


class PostgresConfig(BaseConfig):
    PG_HOST: str = "localhost"
    PG_PORT: int = 5433
    PG_DATABASE: str = "test_database"
    PG_USER: str = "app"
    PG_PASSWORD: str = "123qwe"

    class Config:
        env_file = ".env"
        env_prefix = "POSTGRES_"


BATCH_SIZE = 10_000
USER_FILM_RATINGS_TABLE = "ratings"
REVIEWS_TABLE = "reviews"
BOOKMARKS_TABLE = "bookmarks"


def create_batch(iterable, n=1):
    batch = []
    for elem in iterable:
        batch.append(elem)
        if len(batch) % n == 0:
            yield batch
            batch = []
    if batch:
        yield batch


def create_tables():
    conn = psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DATABASE,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
    )
    cursor = conn.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {USER_FILM_RATINGS_TABLE} (
            user_id UUID PRIMARY KEY,
            film_id UUID,
            rating SMALLINT,
            date_created TIMESTAMP
        )
    """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {REVIEWS_TABLE} (
            user_id UUID PRIMARY KEY,
            film_id UUID,
            text TEXT,
            date_created TIMESTAMP
        )
    """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {BOOKMARKS_TABLE} (
            user_id UUID PRIMARY KEY,
            film_id UUID,
            date_created TIMESTAMP
        )
    """
    )

    conn.commit()
    cursor.close()
    conn.close()


def insert_data_into_table(table_name, data: list[dict]):
    conn = psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DATABASE,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
    )
    cursor = conn.cursor()

    for item in data:
        columns = ", ".join(item.keys())
        placeholders = ", ".join(["%s"] * len(item))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(item.values()))

    conn.commit()
    cursor.close()
    conn.close()


def get_table_counts():
    conn = psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DATABASE,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
    )
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {USER_FILM_RATINGS_TABLE}")
    user_film_ratings_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {REVIEWS_TABLE}")
    reviews_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {BOOKMARKS_TABLE}")
    bookmarks_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return user_film_ratings_count, reviews_count, bookmarks_count


def user_film_insert(num):
    user_film_ratings = create_user_film_ratings(num)
    for counter, batch in enumerate(create_batch(user_film_ratings, BATCH_SIZE), start=1):
        insert_data_into_table(USER_FILM_RATINGS_TABLE, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def reviews_insert(num):
    reviews = create_reviews(num)
    for counter, batch in enumerate(create_batch(reviews, BATCH_SIZE), start=1):
        insert_data_into_table(REVIEWS_TABLE, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def bookmarks_insert(num):
    bookmarks = create_bookmarks(num)
    for counter, batch in enumerate(create_batch(bookmarks, BATCH_SIZE), start=1):
        insert_data_into_table(BOOKMARKS_TABLE, [item.__dict__ for item in batch])
        print(BATCH_SIZE * counter, "rows inserted")


def main():
    num_elements = 15 * 1_000_000

    global config
    config = PostgresConfig()

    create_tables()

    user_film_insert(num_elements)
    print(f"Data is inserted to table {USER_FILM_RATINGS_TABLE}")

    reviews_insert(num_elements)
    print(f"Data is inserted to table {REVIEWS_TABLE}")

    bookmarks_insert(num_elements)
    print(f"Data is inserted to table {BOOKMARKS_TABLE}")

    print(f"{20 * '='}\nData insertion completed successfully!")

    user_film_ratings_count, reviews_count, bookmarks_count = get_table_counts()
    print(f"Table '{USER_FILM_RATINGS_TABLE}' count: {user_film_ratings_count}")
    print(f"Table '{REVIEWS_TABLE}' count: {reviews_count}")
    print(f"Table '{BOOKMARKS_TABLE}' count: {bookmarks_count}")


if __name__ == "__main__":
    main()
