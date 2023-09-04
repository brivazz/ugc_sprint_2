"""Модуль для взаимодействия пользователя с закладками фильмов."""

from uuid import UUID

from api.utils.extensions import is_authenticated
from api.utils.response_models import FilmFormBookmarks
from fastapi import APIRouter, Depends, HTTPException, Response, status
from services.film_bookmarks import BookmarksService, get_bookmark_service

router = APIRouter()


@router.get('/', response_model=list[FilmFormBookmarks])
async def get_film_bookmarks(  # type: ignore[no-untyped-def]
    token_sub=Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> list[FilmFormBookmarks] | dict[str, str]:
    """Возвращает закладки фильмов пользователя."""
    user_id = token_sub.get('user_id')
    films_ids = await bookmark_service.get_bookmark_films(user_id)
    if films_ids is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='bookmarks not found')
    return [FilmFormBookmarks(film_id=film_id) for film_id in films_ids]


@router.post('/{film_id}')
async def add_film_to_bookmark(  # type: ignore[no-untyped-def]
    film_id: UUID,
    token_sub=Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> str | dict[str, str]:
    """Добавляет фильм в закладки."""
    user_id = token_sub.get('user_id')
    result = await bookmark_service.add_film_to_bookmarks(film_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='entry not added')
    return Response(status_code=status.HTTP_201_CREATED, content='Ok')  # type: ignore[no-any-return]


@router.delete('/{film_id}')
async def delete_film_from_bookmark(  # type: ignore[no-untyped-def]
    film_id: UUID,
    token_sub=Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> str | dict[str, str]:
    """Удаляет фильм из закладки."""
    user_id = token_sub.get('user_id')
    result = await bookmark_service.delete_film_from_bookmarks(film_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='bookmarks not found')
    return Response(status_code=status.HTTP_200_OK, content='Ok')  # type: ignore[no-any-return]
