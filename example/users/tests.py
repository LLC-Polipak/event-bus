"""Интеграционные тесты публикации метаданных событий через HTTP API."""

from django.test import Client


def test_registered_user_event_is_available_in_event_list(client: Client) -> None:
    """Вернуть описание user.created в списке зарегистрированных событий."""
    response = client.get('/api/v1/events/')

    assert response.status_code == 200
    assert response.json() == [
        {
            'code': 'user.created',
            'title': 'Пользователь создан',
            'description': 'Событие, публикуемое после создания пользователя.',
            'target': 'users.events.UserCreated',
            'fields': [
                {
                    'name': 'user_id',
                    'annotation': 'int',
                    'required': True,
                    'default': None,
                },
                {
                    'name': 'email',
                    'annotation': 'str',
                    'required': True,
                    'default': None,
                },
            ],
        },
    ]


def test_event_list_is_rendered_in_browser(client: Client) -> None:
    """Отобразить browsable API без ошибки отсутствующего DRF-шаблона."""
    response = client.get(
        '/api/v1/events/',
        headers={'accept': 'text/html'},
    )

    assert response.status_code == 200
    assert 'user.created' in response.content.decode()
