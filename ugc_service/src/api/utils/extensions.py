"""Вспомогательный модуль для аутентификации и пагинации."""

import json
from http import HTTPStatus

import httpx
import jwt
from core.config import settings
from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPBearer

bearer = HTTPBearer()


async def is_authenticated(token: HTTPBearer = Depends(bearer)) -> dict[str, str]:
    """Аутентифицирует пользователя."""
    url = f'{settings.auth_server_url}/is_authenticated'
    headers = {'Authorization': f'Bearer {token.credentials}'}
    # return {'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}  # type: ignore
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        status_code = response.status_code
    if status_code == HTTPStatus.UNAUTHORIZED:
        raise HTTPException(status_code=401, detail='You are not authenticated')
    if status_code != HTTPStatus.OK:
        raise HTTPException(status_code=500, detail='Something was broke')

    token_inf = jwt.decode(token.credentials, options={'verify_signature': False})
    return json.loads(token_inf['sub'])  # type: ignore[no-any-return]


class PaginateQueryParams:
    """Класс для разделения ответов на страницы."""

    def __init__(
        self,
        page_number: int = Query(
            1,
            title='Page number.',
            description='Номер страницы (начиная с 1)',
            gt=0,
        ),
        page_size: int = Query(
            50,
            title='Size of page.',
            description='Количество записей на странице (от 1 до 100)',
            gt=0,
            le=100,
        ),
    ):
        """Инициализирует класс пагинации ответов."""
        self.page_number = page_number
        self.page_size = page_size
