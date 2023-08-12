import pydantic


class MongoDBConfig(pydantic.BaseModel):
    """Configuration class for MongoDB."""

    mongo_connection_string: str = "mongodb://root:example@localhost:27017/"
    # mongo_connection_string: str = "mongodb://root:example@mongo:27017/"
    db_name: str = "someDb"

    # num_elements: int = 15 * 1_000_000
    num_elements: int = 10
    # batch_size: int = 10_000
    batch_size: int = 3
    film_ratings_collection: str = "film_ratings"
    reviews_collection: str = "reviews"
    bookmarks_collection: str = "bookmarks"


mongo_cfg = MongoDBConfig()
