"""Генерирует тестовые логи и записывает в файл."""

import datetime
import json
import sys
from pathlib import Path
from typing import Any

import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from loguru import logger  # type: ignore

app = FastAPI()


base_dir: Path = Path(__file__).resolve().parent
log_dir: Path = Path(base_dir).resolve().parent

log_file_path = Path.joinpath(log_dir, 'logs/fastapi/access.log')
err_log_file_path = Path.joinpath(log_dir, 'logs/fastapi/errors.log')

# logger.remove()
# logger.add(
#     # '/var/log/file.log',
#     'debug.log',
#     format=formatter,
#     rotation='500 MB',
# )


def serialize(record: dict) -> dict[str, str]:
    subset = {
        '@timestamp': str(record['time']),
        'level': record['level'].name,
        'file': record['file'].name + ':' + record['function'] + ':' + str(record['line']),
        'message': record['message'],
    }
    return json.dumps(subset)


def formatter(record: dict) -> str:
    record['extra']['serialized'] = serialize(record)
    return '{extra[serialized]}\n'


loguru_config = {
    'handlers': [
        {
            'sink': sys.stderr,
            'level': 'INFO',
            'colorize': True,
            'format': '<green>{time:YYYY-mm-dd HH:mm:ss.SSS}</green>'
            '| {thread.name} | <level>{level}</level> | '
            '<cyan>{module}</cyan>:<cyan>{function}</cyan>:'
            '<cyan>{line}</cyan> - <level>{message}</level>',
        },
        {'sink': log_file_path, 'format': formatter, 'rotation': '500 MB', 'encoding': 'utf-8'},
        {
            'sink': err_log_file_path,
            'level': 'ERROR',
            'serialize': False,
            'diagnose': False,  # True - подробный отчет
            'backtrace': True,
            'retention': '7 days',
            'rotation': '500 MB',
            'encoding': 'utf-8',
        },
    ],
}
# logger.remove()
logger.configure(**loguru_config)


def generate_log_message() -> dict[str, Any]:
    """
    Генерирует сообщения журнала.

    Returns:
        dict: Словарь лога.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(  # type: ignore
        timespec='milliseconds',
        sep=' ',
    )
    message = 'This is a sample log message'
    if a := 1:
        try:
            10 / 0
        except Exception as e:
            logger.exception(e)
    logger.info(message)

    return {'@timestamp': timestamp, 'message': message}


@app.get('/')
async def write_log_file() -> dict[str, Any]:
    """
    Записывает файл лога в каталог.

    Returns:
        dict: Сгенерированное сообщение лога.
    """
    return generate_log_message()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
