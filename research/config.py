import pydantic  # type: ignore


class MongoDBConfig(pydantic.BaseModel):
    """Configuration class for MongoDB."""

    mongo_connection_string: str = "mongodb://root:example@localhost:27017/"  # pragma: allowlist secret
    # mongo_connection_string: str = "mongodb://root:example@mongo:27017/"  # pragma: allowlist secret
    db_name: str = "someDb"

    # num_elements: int = 15 * 1_000_000
    num_elements: int = 10
    # batch_size: int = 10_000
    batch_size: int = 3
    film_ratings_collection: str = "film_ratings"
    reviews_collection: str = "reviews"
    bookmarks_collection: str = "bookmarks"


class PostgresConfig(pydantic.BaseModel):
    PG_HOST: str = "localhost"
    PG_PORT: int = 5433
    PG_DATABASE: str = "test_database"
    PG_USER: str = "app"
    PG_PASSWORD: str = "123qwe"

    batch_size = 10_000
    film_ratings_table = "ratings"
    reviews_table = "reviews"
    bookmarks_table = "bookmarks"


mongo_cfg = MongoDBConfig()
postgres_cfg = PostgresConfig()
