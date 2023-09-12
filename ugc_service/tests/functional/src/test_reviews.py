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
        # добавление отзыва успешное
        (
            {
                'content': [{'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}],
                'request_body': {'film_score': 10, 'review_text': 'Greatest film'},
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_review': {'status': HTTPStatus.CREATED, 'message': {'message': 'Ok'}},
                'get_review': {
                    'status': HTTPStatus.OK,
                    'message': {
                        'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        'review_text': 'Greatest film',
                        'film_score': 10,
                    },
                },
                'update_review': {
                    'status': HTTPStatus.OK,
                    'message': {
                        'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        'review_text': 'Patched text',
                        'film_score': 5.0,
                    },
                },
                'delete_review': {'status': HTTPStatus.OK, 'message': {'message': 'Ok'}},
            },
        ),
        # добавление отзыва повторное
        (
            {
                'content': [
                    {'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                    {'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                ],
                'request_body': {'film_score': 10, 'review_text': 'Greatest film'},
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_review': {'status': HTTPStatus.BAD_REQUEST, 'message': {'detail': 'Review is not add.'}},
                'get_review': {
                    'status': HTTPStatus.OK,
                    'message': {
                        'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        'review_text': 'Greatest film',
                        'film_score': 10,
                    },
                },
                'update_review': {
                    'status': HTTPStatus.OK,
                    'message': {
                        'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        'review_text': 'Patched text',
                        'film_score': 5.0,
                    },
                },
                'delete_review': {'status': HTTPStatus.OK, 'message': {'message': 'Ok'}},
            },
        ),
        # добавление отзыва с ошибками
        (
            {
                'content': [{'film_id': '5717-4562-b3fc-2c963f66afa6'}],
                'request_body': {'review_text': 'string', 'film_score': 10},
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'add_review': {
                    'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                    'message': 'Input should be a valid UUID, unable to parse string as an UUID',
                },
                'get_review': {
                    'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                    'message': 'Input should be a valid UUID, unable to parse string as an UUID',
                },
                'update_review': {
                    'status': HTTPStatus.BAD_REQUEST,
                    'message': {'detail': 'Review not update'},
                },
                'delete_review': {'status': HTTPStatus.BAD_REQUEST, 'message': {'detail': 'Review not delete'}},
            },
        ),
    ],
)
async def test_reviews(make_get_request, query_data: dict, expected_answer: dict):
    url = f'{settings_test.service_url}/api/v1/ugc_2/film_reviews/'
    headers = {'Authorization': f"Bearer {query_data['token']}"}
    for film in query_data['content']:
        message, status = await make_get_request(
            url + film['film_id'],
            data=query_data['request_body'],
            method='POST',
            headers=headers,
        )
    assert status == expected_answer['add_review']['status']

    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        if 'msg' in message.get('detail')[-1]:
            assert message.get('detail')[-1]['msg'] == expected_answer['add_review']['message']
        else:
            assert message == expected_answer['add_review']['message']

    message, status = await make_get_request(url + film['film_id'], method='GET', headers=headers)
    assert status == expected_answer['get_review']['status']
    if status == HTTPStatus.OK:
        assert message[0].get('user_id') == expected_answer['get_review']['message']['user_id']
        assert message[0].get('review_text') == expected_answer['get_review']['message']['review_text']
        assert message[0].get('film_score') == expected_answer['get_review']['message']['film_score']

    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        if 'msg' in message.get('detail')[-1]:
            assert message.get('detail')[-1]['msg'] == expected_answer['get_review']['message']
        else:
            assert message == expected_answer['get_review']['message']

    if type(message) == list:
        review_id = message[0].get('review_id')
        patch_data = {
            'review_text': expected_answer['update_review']['message']['review_text'],
            'film_score': expected_answer['update_review']['message']['film_score'],
        }
    else:
        review_id = '64df5a03284cd4cb985effbb'
        patch_data = {'review_text': 'string', 'film_score': 1}

    message, status = await make_get_request(url + review_id, method='PATCH', data=patch_data, headers=headers)
    assert status == expected_answer['update_review']['status']
    if status == HTTPStatus.OK:
        assert message.get('user_id') == expected_answer['update_review']['message']['user_id']
        assert message.get('review_text') == expected_answer['update_review']['message']['review_text']
        assert message.get('film_score') == expected_answer['update_review']['message']['film_score']
    if status == HTTPStatus.BAD_REQUEST:
        assert message == expected_answer['update_review']['message']

    message, status = await make_get_request(url + review_id, method='DELETE', headers=headers)
    assert status == expected_answer['delete_review']['status']
    assert message == expected_answer['delete_review']['message']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # успешное удаление оценки из коллекции film_scores
        (
            {
                'content': [
                    {
                        'film_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        'film_score': 10,
                    }
                ],
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX2lkXCI6IFwiMzc3YmU3ZmEtODM5Ni00M2Y4LWFlNDYtMzc4NDE1YWRkNWUwXCJ9In0._vmq_o4hELki8rKXOzJSFOIpE8SsFs8escRseBpgsyU',
            },
            {
                'delete_scores': {'status': HTTPStatus.OK, 'message': {'message': 'Ok'}},
            },
        ),
    ],
)
async def test_delete_film_scores(make_get_request, query_data: dict, expected_answer: dict):
    url = f'{settings_test.service_url}/api/v1/ugc_2/film_score/'
    headers = {'Authorization': f"Bearer {query_data['token']}"}
    message, status = await make_get_request(
        url + query_data['content'][-1]['film_id'], method='DELETE', headers=headers
    )
    assert status == expected_answer['delete_scores']['status']
    assert message == expected_answer['delete_scores']['message']
