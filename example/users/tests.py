"""Интеграционные тесты публикации метаданных событий через HTTP API."""

from django.test import Client

from users.events import (
    Address,
    NotificationSettings,
    UserProfile,
    UserProfileUpdated,
)


def test_registered_user_event_is_available_in_event_list(client: Client) -> None:
    """Вернуть описание user.created в списке зарегистрированных событий."""
    response = client.get('/api/v1/events/')

    assert response.status_code == 200
    events = response.json()

    assert events[0] == {
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
    }
    assert events[1] == {
        'code': 'user.profile.updated',
        'title': 'Профиль пользователя обновлён',
        'description': (
            'Событие с вложенным объектом профиля и произвольными метаданными.'
        ),
        'target': 'users.events.UserProfileUpdated',
        'fields': [
            {
                'name': 'user_id',
                'annotation': 'int',
                'required': True,
                'default': None,
            },
            {
                'name': 'profile',
                'annotation': 'UserProfile',
                'required': True,
                'default': None,
                'fields': [
                    {
                        'name': 'name',
                        'annotation': 'str',
                        'required': True,
                        'default': None,
                    },
                    {
                        'name': 'address',
                        'annotation': 'Address',
                        'required': True,
                        'default': None,
                        'fields': [
                            {
                                'name': 'city',
                                'annotation': 'str',
                                'required': True,
                                'default': None,
                            },
                            {
                                'name': 'street',
                                'annotation': 'str',
                                'required': True,
                                'default': None,
                            },
                        ],
                    },
                    {
                        'name': 'notifications',
                        'annotation': 'NotificationSettings',
                        'required': True,
                        'default': None,
                        'fields': [
                            {
                                'name': 'email',
                                'annotation': 'bool',
                                'required': True,
                                'default': None,
                            },
                            {
                                'name': 'sms',
                                'annotation': 'bool',
                                'required': True,
                                'default': None,
                            },
                        ],
                    },
                    {
                        'name': 'roles',
                        'annotation': 'list[str]',
                        'required': True,
                        'default': None,
                    },
                ],
            },
            {
                'name': 'metadata',
                'annotation': 'dict[str, str]',
                'required': True,
                'default': None,
            },
        ],
    }


def test_nested_event_objects_are_converted_to_payload_dicts() -> None:
    """Преобразовать вложенный профиль в JSON-совместимый payload."""
    event = UserProfileUpdated(
        user_id=123,
        profile=UserProfile(
            name='Иван',
            address=Address(city='Москва', street='Тверская'),
            notifications=NotificationSettings(email=True, sms=False),
            roles=['customer', 'subscriber'],
        ),
        metadata={'request_id': 'request-42'},
    )

    assert event.payload() == {
        'user_id': 123,
        'profile': {
            'name': 'Иван',
            'address': {'city': 'Москва', 'street': 'Тверская'},
            'notifications': {'email': True, 'sms': False},
            'roles': ['customer', 'subscriber'],
        },
        'metadata': {'request_id': 'request-42'},
    }


def test_event_list_is_rendered_in_browser(client: Client) -> None:
    """Отобразить browsable API без ошибки отсутствующего DRF-шаблона."""
    response = client.get(
        '/api/v1/events/',
        headers={'accept': 'text/html'},
    )

    assert response.status_code == 200
    assert 'user.created' in response.content.decode()
