"""Модуль с настройкой логгирования."""

import json
import sys
import typing
from pathlib import Path

from core.config import settings
from loguru import logger

logs_dir: Path = Path(settings.base_dir).resolve().parent.parent
log_file_path = Path.joinpath(logs_dir, '/var/log/access.log')
err_log_file_path = Path.joinpath(logs_dir, '/var/log/errors.log')


def serialize(record: dict[str, typing.Any]) -> str:
    """Сериализует запись лога в формат JSON."""
    subset = {
        '@timestamp': str(record['time']),
        'level': record['level'].name,
        'file': record['file'].name + ':' + record['function'] + ':' + str(record['line']),
        'message': record['message'],
    }
    return json.dumps(subset)


def formatter(record: dict[str, typing.Any]) -> str:
    """Функция пользовательского форматирования логов."""
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
        {'sink': log_file_path, 'format': formatter, 'enqueue': True, 'rotation': '50 MB', 'encoding': 'utf-8'},
        {
            'sink': err_log_file_path,
            'level': 'ERROR',
            'serialize': False,
            'diagnose': False,  # True - подробный отчет
            'backtrace': True,
            'retention': '7 days',
            'rotation': '50 MB',
            'encoding': 'utf-8',
        },
    ],
}
logger.configure(**loguru_config)
