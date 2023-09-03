"""Модуль сервиса для работы с закладками фильмов."""

from functools import lru_cache
from uuid import UUID

from db.mongo.mongo_rep import MongoRepository, get_mongo_repository
from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError


class BookmarksService:
    """Сервис для работы с закладками фильмов в MongoDB."""

    def __init__(self, mongo_repository: MongoRepository) -> None:
        """Инициализирует сервис закладок фильмов с указанным репозиторием MongoDB."""
        self._mongo_repository = mongo_repository
        self.collection_name = 'film_bookmarks'

    async def get_bookmark_films(self, user_id: UUID) -> list[dict[str, UUID]] | None:
        """Возвращает список id фильмов, добавленных пользователем в закладки."""
        films_bookmarks = await self._mongo_repository.find_all(self.collection_name, {'user_id': user_id})
        if films_bookmarks:
            return [film_obj.get('film_id') for film_obj in films_bookmarks]
        return None

    async def add_film_to_bookmarks(self, film_id: UUID, user_id: UUID) -> str | None:
        """Добавляет фильм в закладки."""
        try:
            return await self._mongo_repository.insert_one(  # type: ignore[no-any-return]
                'film_bookmarks',
                {'film_id': str(film_id), 'user_id': str(user_id)},
            )
        except DuplicateKeyError as er:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='the movie has already been added to bookmarks',
            ) from er

    async def delete_film_from_bookmarks(self, film_id: UUID, user_id: UUID) -> int | None:
        """Удаляет фильм из закладок пользователя."""
        return await self._mongo_repository.delete_one(  # type: ignore[no-any-return]
            self.collection_name,
            {'film_id': str(film_id), 'user_id': str(user_id)},
        )


@lru_cache
def get_bookmark_service(repository=Depends(get_mongo_repository)) -> BookmarksService:  # type: ignore[no-untyped-def]
    """Возвращает экземпляр сервиса для работы с закладками фильмов."""
    return BookmarksService(repository)
