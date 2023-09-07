"""Модуль для взаимодействия пользователя с закладками фильмов."""

import json
import typing
import uuid

from api.utils.extensions import is_authenticated
from api.utils.response_models import FilmFormBookmarks
from fastapi import APIRouter, Depends, HTTPException, Response, status
from services.film_bookmarks import BookmarksService, get_bookmark_service

router = APIRouter()


@router.get('/', response_model=list[FilmFormBookmarks])
async def get_film_bookmarks(
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> list[FilmFormBookmarks] | dict[str, str]:
    """Возвращает закладки фильмов пользователя."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    films_ids = await bookmark_service.get_bookmark_films(user_id)
    if films_ids is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='bookmarks not found')
    return [FilmFormBookmarks(film_id=film_id) for film_id in films_ids]


@router.post('/{film_id}')
async def add_film_to_bookmark(
    film_id: uuid.UUID,
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> str | dict[str, str]:
    """Добавляет фильм в закладки."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await bookmark_service.add_film_to_bookmarks(film_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='entry not added')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_201_CREATED,
        content=json.dumps({'message': 'Ok'}),
        media_type='application/json',
    )


@router.delete('/{film_id}')
async def delete_film_from_bookmark(
    film_id: uuid.UUID,
    token_sub: dict[str, str] = Depends(is_authenticated),
    bookmark_service: BookmarksService = Depends(get_bookmark_service),
) -> str | dict[str, typing.Any]:
    """Удаляет фильм из закладки."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await bookmark_service.delete_film_from_bookmarks(film_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='bookmarks not found')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_200_OK,
        content=json.dumps({'message': 'Ok'}),
        media_type='application/json',
    )
