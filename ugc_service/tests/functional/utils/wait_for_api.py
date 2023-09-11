import http
import os
import sys
import time

import requests
from loguru import logger

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings_test

if __name__ == '__main__':
    while True:
        try:
            response = requests.get(f'{settings_test.service_url}/api/v1/ugc_2/openapi#/')
            if response.status_code == http.HTTPStatus.OK:
                logger.info('Services is available!!')
                break
        except requests.exceptions.ConnectionError:
            logger.info('Api is unavailable. Wait...')
        time.sleep(2)
