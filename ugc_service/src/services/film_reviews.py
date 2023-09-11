"""Модуль сервиса для работы с отзывами фильмов."""

import datetime
import uuid
from functools import lru_cache

import bson
from db.mongo.mongo_rep import MongoRepository, get_mongo_repository
from fastapi import Depends


class FilmReviewsService:
    """Сервис для работы с отзывами фильмов в MongoDB."""

    def __init__(self, mongo_repository: MongoRepository):
        """Инициализирует сервис отзывов о фильмах."""
        self._mongo_repository = mongo_repository
        self.collection_name = 'film_reviews'

    async def add_review(
        self,
        film_id: uuid.UUID,
        review_text: str,
        user_id: uuid.UUID,
        film_score: float,
        create_at: datetime.datetime,
    ) -> str | None:
        """Добавляет отзыв и оценку фильма."""
        document = {
            'film_id': str(film_id),
            'user_id': str(user_id),
            'review_text': review_text,
            'film_score': str(film_score),
            'create_at': create_at,
            'update_at': datetime.datetime.now(),
        }
        result = await self._mongo_repository.insert_one(self.collection_name, document)
        if result:
            existing_film_score = await self._mongo_repository.find_one(
                'film_score',
                {'film_id': str(film_id), 'user_id': str(user_id)},
            )
            if existing_film_score and film_score:
                await self._mongo_repository.update_one(
                    'film_score',
                    existing_film_score,
                    {'film_score': str(film_score)},
                )
            elif film_score:
                await self._mongo_repository.insert_one(
                    'film_score',
                    {
                        'film_id': str(film_id),
                        'user_id': str(user_id),
                        'film_score': film_score,
                    },
                )
        return result  # type: ignore[no-any-return]

    async def update_review(
        self,
        user_id: uuid.UUID,
        review_id: str,
        new_review_text: str | None,
        new_film_score: float | None,
    ) -> dict[str, str] | None:
        """Редактирует озыв и оценку фильма."""
        result = existing_film_review = await self._mongo_repository.find_one(
            self.collection_name,
            {'_id': bson.ObjectId(review_id), 'user_id': str(user_id)},
        )
        if result:
            result = await self._mongo_repository.update_one(
                self.collection_name,
                existing_film_review,
                {
                    'update_at': datetime.datetime.now()
                    if new_review_text or new_film_score
                    else existing_film_review['update_at'],
                    'review_text': new_review_text or existing_film_review['review_text'],
                    'film_score': new_film_score or existing_film_review['film_score'],
                },
            )
        if new_film_score and result:
            await self._mongo_repository.update_one(
                'film_score',
                {'film_id': existing_film_review['film_id'], 'user_id': existing_film_review['user_id']},
                {'film_score': new_film_score},
            )
        return result  # type: ignore[no-any-return]

    async def delete_review(self, review_id: str, user_id: uuid.UUID) -> None | int:
        """Удаляет отзыв о фильме."""
        return await self._mongo_repository.delete_one(  # type: ignore[no-any-return]
            self.collection_name,
            {'_id': bson.ObjectId(review_id), 'user_id': str(user_id)},
        )

    async def get_reviews_for_film(
        self,
        film_id: uuid.UUID,
        page_number: int = 1,
        page_size: int = 50,
    ) -> list[dict[str, str]]:
        """Возвращает список отзвов о фильме."""
        return await self._mongo_repository.find_all(  # type: ignore[no-any-return]
            self.collection_name,
            {'film_id': str(film_id)},
            page_number=page_number,
            page_size=page_size,
        )


@lru_cache
def get_film_review_service(
    repository: MongoRepository = Depends(get_mongo_repository),
) -> FilmReviewsService:
    """Возвращает экземпляр сервиса для работы с отзывами фильмов."""
    return FilmReviewsService(repository)
