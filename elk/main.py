"""Генерирует тестовые логи и записывает в файл."""

import datetime
from typing import Any

import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from loguru import logger  # type: ignore

app = FastAPI()

logger.add(
    "/var/log/file.log",
    format="{message}",
    rotation="500 MB",
)


def generate_log_message() -> dict[str, Any]:
    """
    Генерирует сообщения журнала.

    Returns:
        dict: Словарь лога.
    """
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(  # type: ignore
        timespec="milliseconds",
        sep=" ",
    )
    message = "This is a sample log message"
    log_message = {"@timestamp": timestamp, "message": message}
    logger.info(log_message)

    return log_message


@app.get("/")
async def write_log_file() -> dict[str, Any]:
    """
    Записывает файл лога в каталог.

    Returns:
        dict: Сгенерированное сообщение лога.
    """
    return generate_log_message()


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)