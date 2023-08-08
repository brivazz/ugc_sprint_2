from dataclasses import dataclass
import uuid
import random
import datetime


@dataclass
class UserFilmRating:
    user_id: str
    film_id: str
    rating: int
    date_created: datetime.datetime


@dataclass
class Review:
    user_id: str
    film_id: str
    text: str
    date_created: datetime.datetime


@dataclass
class Bookmark:
    user_id: str
    film_id: str
    date_created: datetime.datetime


def generate_uuid():
    return str(uuid.uuid4())


def generate_rating():
    return random.randint(0, 10)


def generate_timestamp():
    return datetime.datetime.now(datetime.timezone.utc)


def create_user_film_ratings(num_elements):
    for _ in range(num_elements):
        yield UserFilmRating(
            user_id=generate_uuid(),
            film_id=generate_uuid(),
            rating=generate_rating(),
            date_created=generate_timestamp(),
        )


def create_reviews(num_elements):
    for _ in range(num_elements):
        yield Review(
            user_id=generate_uuid(),
            film_id=generate_uuid(),
            text="This movie is great!",
            date_created=generate_timestamp(),
        )


def create_bookmarks(num_elements):
    for _ in range(num_elements):
        yield Bookmark(
            user_id=generate_uuid(),
            film_id=generate_uuid(),
            date_created=generate_timestamp(),
        )


def get_likes_bookmarks_reviews(number_rows):
    likes = create_user_film_ratings(number_rows)
    bookmarks = create_bookmarks(number_rows)
    reviews = create_reviews(number_rows)
    return likes, bookmarks, reviews
