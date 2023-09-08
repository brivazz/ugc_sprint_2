"""Модуль для взаимодействия пользователя с оценками фильмов."""

import typing
import uuid

import orjson
from api.utils.extensions import is_authenticated
from api.utils.response_models import FilmAverageScore, FilmScore
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from services.film_score import FilmScoreService, get_film_score_service

router = APIRouter()


@router.get('/{film_id}', response_model=FilmAverageScore)
async def get_film_score(
    film_id: uuid.UUID = Path(title='UUID фильма', example='a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'),
    score_service: FilmScoreService = Depends(get_film_score_service),
) -> FilmAverageScore:
    """Получает среднюю оценку фильма по его id."""
    average_film_score = await score_service.get_score(film_id)
    if average_film_score is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Фильм еще никто не оценил')
    return FilmAverageScore(average_film_score=average_film_score)


@router.post('/')
async def add_film_score(
    film_score: FilmScore = Body(),
    score_service: FilmScoreService = Depends(get_film_score_service),
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
) -> str:
    """Добавляет оценку к фильму."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await score_service.add_score(film_score.film_id, user_id, film_score.film_score)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='error when adding a record')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_201_CREATED,
        content=orjson.dumps({'message': 'Ok'}),
        media_type='application/json',
    )


@router.delete('/{film_id}')
async def delete_film_score(
    film_id: uuid.UUID = Path(title='UUID фильма', example='a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'),
    score_service: FilmScoreService = Depends(get_film_score_service),
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
) -> str:
    """Удаляет оценку фильма по его id."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await score_service.delete_score(film_id, user_id)
    if result is None or result == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='error deleting a record')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_200_OK,
        content=orjson.dumps({'message': 'Ok'}),
        media_type='application/json',
    )
