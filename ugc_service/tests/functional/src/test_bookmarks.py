import os
import sys
from http import HTTPStatus

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings_test

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # добавление фильма в закладки успешное
        (
            {
                'content': [{'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}],
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_bookmark': {'status': HTTPStatus.CREATED, 'message': 'Ok'},
                'get_bookmark': {
                    'status': HTTPStatus.OK,
                    'message': [{'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}],
                },
                'delete_bookmark': {'status': HTTPStatus.OK, 'message': 'Ok'},
            },
        ),
        # добавление фильма в закладки повторное
        (
            {
                'content': [
                    {'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                    {'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                ],
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_bookmark': {
                    'status': HTTPStatus.BAD_REQUEST,
                    'message': {'detail': 'the movie has already been added to bookmarks'},
                },
                'get_bookmark': {
                    'status': HTTPStatus.OK,
                    'message': [{'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}],
                },
                'delete_bookmark': {'status': HTTPStatus.OK, 'message': 'Ok'},
            },
        ),
        # добавление фильма c ошибками
        (
            {
                'content': [{'film_id': 'not_uuid'}],
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_bookmark': {
                    'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                    'message': 'Input should be a valid UUID, unable to parse string as an UUID',
                },
                'get_bookmark': {'status': HTTPStatus.NOT_FOUND, 'message': {'detail': 'bookmarks not found'}},
                'delete_bookmark': {
                    'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                    'message': 'Input should be a valid UUID, unable to parse string as an UUID',
                },
            },
        ),
    ],
)
async def test_bookmarks(make_get_request, query_data: dict, expected_answer: dict):
    url = f'{settings_test.service_url}/api/v1/ugc_2/film_bookmarks/'
    headers = {'Authorization': f"Bearer {query_data['token']}"}
    for film in query_data['content']:
        message, status = await make_get_request(url + film['film_id'], method='POST', headers=headers)
    assert status == expected_answer['add_bookmark']['status']
    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        if 'msg' in message.get('detail')[-1]:
            assert message.get('detail')[-1]['msg'] == expected_answer['add_bookmark']['message']
        else:
            assert message == expected_answer['add_bookmark']['message']

    message, status = await make_get_request(url, method='GET', headers=headers)
    assert status == expected_answer['get_bookmark']['status']
    assert message == expected_answer['get_bookmark']['message']

    message, status = await make_get_request(
        url + query_data['content'][-1]['film_id'], method='DELETE', headers=headers
    )
    assert status == expected_answer['delete_bookmark']['status']
    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        if 'msg' in message.get('detail')[-1]:
            assert message.get('detail')[-1]['msg'] == expected_answer['delete_bookmark']['message']
        else:
            assert message == expected_answer['delete_bookmark']['message']
