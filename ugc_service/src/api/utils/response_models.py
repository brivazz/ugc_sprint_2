# Из-за того, что mypy ругается на
# error: Class cannot subclass "BaseModel" (has type "Any")  [misc]
# из-за новой версии pydantic v2, игнор всего файла

# mypy: ignore-errors

"""Модуль с моделями ответов api."""

import datetime
import uuid

from pydantic import BaseModel, Field


class FilmFormBookmarks(BaseModel):
    """Модель для добавления закладки фильма."""

    film_id: uuid.UUID


class FilmReviewResponse(BaseModel):
    """Модель ответа пользователю о рецензии и оценке фильма."""

    review_id: str
    user_id: uuid.UUID
    review_text: str
    film_score: float | None = Field(..., ge=0, le=10)
    create_at: datetime.datetime
    update_at: datetime.datetime


class FilmReviewRequest(BaseModel):
    """Модель для добавления отзыва и оценки фильма."""

    review_text: str
    film_score: float = Field(..., ge=0, le=10)


class ReviewUpdate(BaseModel):
    """Модель для обновления отзыва и оценки фильма."""

    review_text: str
    film_score: float = Field(..., ge=0, le=10)


class FilmAverageScore(BaseModel):
    """Модель ответа пользователю средней оценки фильма."""

    average_film_score: float


class FilmScore(BaseModel):
    """Модель для добавления оценки фильма."""

    film_id: uuid.UUID
    film_score: float = Field(..., ge=0, le=10)
