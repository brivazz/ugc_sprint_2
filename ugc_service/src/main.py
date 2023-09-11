"""Точка входа в приложение."""

import fastapi

# import sentry_sdk
from api.v1 import film_bookmarks, film_reviews, film_score
from core.config import settings
from core.logger import logger
from db.mongo import mongo_storage  # type: ignore[attr-defined]

# from sentry_sdk.integrations.loguru import LoguruIntegration

# sentry_sdk.init(
#     # dsn=settings.sentry_dsn,  # type: ignore
#     traces_sample_rate=1.0,
#     integrations=[
#         LoguruIntegration(),
#     ],
# )


def init_app() -> fastapi.FastAPI:
    """Инициализирует экземпляр FastAPI."""
    return fastapi.FastAPI(
        title=settings.project_name,
        docs_url='/api/v1/ugc_2/openapi',
        openapi_url='/api/v1/ugc_2/openapi.json',
        default_response_class=fastapi.responses.ORJSONResponse,
        debug=settings.debug,
    )


app = init_app()


@app.on_event('startup')
async def startup() -> None:
    """Выполняет необходимые действия при запуске приложения."""
    logger.info('Fastapi service launched.')
    await mongo_storage.on_startup([f'{settings.mongo_host}:{settings.mongo_port}'])


@app.on_event('shutdown')
async def shutdown() -> None:
    """Выполняет необходимые действия при остановке приложения."""
    mongo_storage.on_shutdown()


app.include_router(film_bookmarks.router, prefix='/api/v1/ugc_2/film_bookmarks', tags=['film_bookmarks'])
app.include_router(film_reviews.router, prefix='/api/v1/ugc_2/film_reviews', tags=['film_reviews'])
app.include_router(film_score.router, prefix='/api/v1/ugc_2/film_score', tags=['film_score'])
