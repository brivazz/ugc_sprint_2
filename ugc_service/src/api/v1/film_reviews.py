"""Модуль для взаимодействия пользователя с отзывами фильмов."""

import datetime
import typing
import uuid

import orjson
from api.utils.extensions import PaginateQueryParams, is_authenticated
from api.utils.response_models import FilmReviewRequest, FilmReviewResponse, ReviewUpdate
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from services.film_reviews import FilmReviewsService, get_film_review_service

router = APIRouter()


@router.get('/{film_id}', response_model=list[FilmReviewResponse])
async def get_film_reviews(
    film_id: uuid.UUID,
    pqp: PaginateQueryParams = Depends(PaginateQueryParams),
    film_review_service: FilmReviewsService = Depends(get_film_review_service),
) -> list[FilmReviewResponse]:
    """Получает отзывы о фильме по его id."""
    film_reviews = await film_review_service.get_reviews_for_film(
        film_id,
        page_number=pqp.page_number,
        page_size=pqp.page_size,
    )
    if not film_reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='film review not found')
    return [FilmReviewResponse(review_id=str(review.get('_id')), **review) for review in film_reviews]


@router.post('/{film_id}')
async def add_film_review(
    film_id: uuid.UUID,
    film_review_request: FilmReviewRequest = Body(),
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
    film_review_service: FilmReviewsService = Depends(get_film_review_service),
) -> str:
    """Добавляет отзыв о фильме по его id."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await film_review_service.add_review(
        film_id=film_id,
        review_text=film_review_request.review_text,
        user_id=user_id,
        film_score=film_review_request.film_score,
        create_at=datetime.datetime.now(),
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review is not add.')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_201_CREATED,
        content=orjson.dumps({'message': 'Ok'}),
        media_type='application/json',
    )


@router.delete('/{review_id}')
async def delete_film_review(
    review_id: str,
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
    film_review_service: FilmReviewsService = Depends(get_film_review_service),
) -> str:
    """Удаляет отзыв о фильме по id отзыва."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    result = await film_review_service.delete_review(user_id=user_id, review_id=review_id)
    if result is None or result == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review not delete')
    return Response(  # type: ignore[no-any-return]
        status_code=status.HTTP_200_OK,
        content=orjson.dumps({'message': 'Ok'}),
        media_type='application/json',
    )


@router.patch('/{review_id}', response_model=FilmReviewResponse)
async def edit_film_review(
    review_id: str,
    review_update: ReviewUpdate,
    token_sub: dict[str, typing.Any] = Depends(is_authenticated),
    film_review_service: FilmReviewsService = Depends(get_film_review_service),
) -> FilmReviewResponse:
    """Редактирует отзыв о фильме по id отзыва."""
    user_id: uuid.UUID = uuid.UUID(token_sub.get('user_id'))
    updated_review = await film_review_service.update_review(
        user_id=user_id,
        review_id=review_id,
        new_review_text=review_update.review_text,
        new_film_score=review_update.film_score,
    )
    if updated_review is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Review not update')
    return FilmReviewResponse(review_id=str(updated_review.get('_id')), **updated_review)
