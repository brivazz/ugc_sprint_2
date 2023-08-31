# Из-за того, что mypy ругается на
# error: Class cannot subclass "BaseModel" (has type "Any")  [misc]
# из-за новой версии pydantic v2, игнор всего файла

# mypy: ignore-errors

"""Модуль с моделями ответов api."""

import datetime
import uuid

from pydantic import BaseModel, Field


class FilmFormBookmarks(BaseModel):
    """Модель ответа пользователю закладка фильма."""

    film_id: uuid.UUID


class FilmReviewResponse(BaseModel):
    """Модель ответа пользователю о рецензии и оценки фильма."""

    review_id: uuid.UUID
    user_id: uuid.UUID
    film_score: float
    text: str
    create_at: datetime.datetime
    update_at: datetime.datetime


class FilmReviewRequest(BaseModel):
    """Модель отзыва и оценки фильма."""

    film_score: float
    review_text: str


class ReviewUpdate(BaseModel):
    """Модель обновления отзыва и оценки фильма."""

    review_text: str | None
    film_score: float | None


class FilmAverageScore(BaseModel):
    """Модель средней оценки фильма."""

    average_film_score: float


class FilmScore(BaseModel):
    """Модель оценки фильма."""

    film_id: uuid.UUID
    film_score: float = Field(..., ge=0, le=10)
