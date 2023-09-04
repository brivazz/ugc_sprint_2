import psycopg2  # type: ignore
from config import postgres_cfg
from fake_data import create_bookmarks, create_film_ratings, create_reviews


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
        host=postgres_cfg.PG_HOST,
        port=postgres_cfg.PG_PORT,
        dbname=postgres_cfg.PG_DATABASE,
        user=postgres_cfg.PG_USER,
        password=postgres_cfg.PG_PASSWORD,
    )
    cursor = conn.cursor()

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {postgres_cfg.film_ratings_table} (
            user_id UUID PRIMARY KEY,
            film_id UUID,
            rating SMALLINT,
            date_created TIMESTAMP
        )
    """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {postgres_cfg.reviews_table} (
            user_id UUID PRIMARY KEY,
            film_id UUID,
            text TEXT,
            date_created TIMESTAMP
        )
    """
    )

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {postgres_cfg.bookmarks_table} (
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
        host=postgres_cfg.PG_HOST,
        port=postgres_cfg.PG_PORT,
        dbname=postgres_cfg.PG_DATABASE,
        user=postgres_cfg.PG_USER,
        password=postgres_cfg.PG_PASSWORD,
    )
    cursor = conn.cursor()

    for item in data:
        columns = ', '.join(item.keys())
        placeholders = ', '.join(['%s'] * len(item))
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        cursor.execute(query, tuple(item.values()))

    conn.commit()
    cursor.close()
    conn.close()


def get_table_counts():
    conn = psycopg2.connect(
        host=postgres_cfg.PG_HOST,
        port=postgres_cfg.PG_PORT,
        dbname=postgres_cfg.PG_DATABASE,
        user=postgres_cfg.PG_USER,
        password=postgres_cfg.PG_PASSWORD,
    )
    cursor = conn.cursor()

    cursor.execute(f'SELECT COUNT(*) FROM {postgres_cfg.film_ratings_table}')
    user_film_ratings_count = cursor.fetchone()[0]

    cursor.execute(f'SELECT COUNT(*) FROM {postgres_cfg.reviews_table}')
    reviews_count = cursor.fetchone()[0]

    cursor.execute(f'SELECT COUNT(*) FROM {postgres_cfg.bookmarks_table}')
    bookmarks_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return user_film_ratings_count, reviews_count, bookmarks_count


def user_film_insert(num):
    user_film_ratings = create_film_ratings(num)
    for counter, batch in enumerate(create_batch(user_film_ratings, postgres_cfg.batch_size), start=1):
        insert_data_into_table(postgres_cfg.film_ratings_table, [item.__dict__ for item in batch])
        print(postgres_cfg.batch_size * counter, 'rows inserted')


def reviews_insert(num):
    reviews = create_reviews(num)
    for counter, batch in enumerate(create_batch(reviews, postgres_cfg.batch_size), start=1):
        insert_data_into_table(postgres_cfg.reviews_table, [item.__dict__ for item in batch])
        print(postgres_cfg.batch_size * counter, 'rows inserted')


def bookmarks_insert(num):
    bookmarks = create_bookmarks(num)
    for counter, batch in enumerate(create_batch(bookmarks, postgres_cfg.batch_size), start=1):
        insert_data_into_table(postgres_cfg.bookmarks_table, [item.__dict__ for item in batch])
        print(postgres_cfg.batch_size * counter, 'rows inserted')


def main():
    num_elements = 15 * 1_000_000

    create_tables()

    user_film_insert(num_elements)
    print(f'Data is inserted to table {postgres_cfg.film_ratings_table}')

    reviews_insert(num_elements)
    print(f'Data is inserted to table {postgres_cfg.reviews_table}')

    bookmarks_insert(num_elements)
    print(f'Data is inserted to table {postgres_cfg.bookmarks_table}')

    print(f"{20 * '='}\nData insertion completed successfully!")

    user_film_ratings_count, reviews_count, bookmarks_count = get_table_counts()
    print(f"Table '{postgres_cfg.film_ratings_table}' count: {user_film_ratings_count}")
    print(f"Table '{postgres_cfg.reviews_table}' count: {reviews_count}")
    print(f"Table '{postgres_cfg.bookmarks_table}' count: {bookmarks_count}")


if __name__ == '__main__':
    main()
