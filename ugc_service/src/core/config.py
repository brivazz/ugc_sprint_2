# Из-за того, что mypy ругается на
# error: Class cannot subclass "BaseSettings" (has type "Any")  [misc]
# из новой версии pydantic v2, игнор всего файла

# mypy: ignore-errors
"""Модуль Конфигурации приложения UGC."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


# type: ignore
class Settings(BaseSettings):
    """Класс, представляющий настройки приложения."""

    project_name: str = Field('movies', env='UGC_2_PROJECT_NAME')
    sentry_url: str = Field(..., env='SENTRY_URL')
    debug: bool = Field(False, env='DEBUG')
    base_dir: Path = Path(__file__).resolve().parent.parent
    auth_server_url: str = Field('http://nginx/api/v1/auth', env='AUTH_URL')

    mongo_db: str = Field('ugc2_movies', env='MONGO_DB')
    mongo_username: str = Field('root', env='MONGO_LOGIN')
    mongo_password: str = Field('example', env='MONGO_PASSWORD')
    mongo_host: str = Field('localhost', env='MONGO_HOST')
    mongo_port: int = Field(27017, env='MONGO_PORT')


settings = Settings()
