# Django Event Bus

Переиспользуемая событийная шина для Django-проектов на базе RabbitMQ.

## Установка

```bash
pip install git+https://github.com/LLC-Polipak/event-bus.git
```

Добавьте Django REST Framework и event bus в `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django applications
    'rest_framework',
    'django_event_bus',
]
```

## Конфигурация

```python
EVENT_BUS = {
    'HOST': 'localhost',
    'PORT': 5672,
    'USER': 'guest',
    'PASSWORD': 'guest',
    'VHOST': '/',
    'SERVICE_NAME': 'my_service',
    'EXCHANGE': 'events',  # optional, default: 'events'
    'API_PATH': 'api/v1/events/',  # optional, default: 'api/v1/events/'
    'CONSUMERS': [
        {
            'enabled': True,
            'source': 'order_service',
            'routing_key': 'order.created',
            'handler': 'myapp.handlers.handle_order_created',
        },
    ],
}
```

`API_PATH` задаёт полный путь до коллекции событий, включая `events/`.
Ведущий `/` необязателен, завершающий `/` добавляется автоматически.

Подключите HTTP API в корневом `urls.py` проекта:

```python
from django.urls import include, path

urlpatterns = [
    path('', include('django_event_bus.urls')),
]
```

При конфигурации выше список событий будет доступен по адресу:

```text
GET /api/v1/events/
```

## Объявление события

Событие должно быть `dataclass`, иметь `event_name` и метод `payload()`.
Декоратор `@event` добавляет его описание в registry:

```python
from dataclasses import asdict, dataclass
from typing import ClassVar

from django_event_bus.event_bus.events import event


@event(code='user.created', title='Пользователь создан')
@dataclass(frozen=True, slots=True)
class UserCreated:
    """Событие создания пользователя."""

    event_name: ClassVar[str] = 'user.created'
    user_id: int
    email: str

    def payload(self) -> dict:
        return asdict(self)
```

Модуль с событиями должен быть импортирован при запуске Django. Например, в `AppConfig.ready()`:

```python
def ready(self) -> None:
    from users import events  # noqa: F401
```

Registry рекурсивно описывает поля вложенных dataclass-объектов. Generic-типы
вроде `list[str]` и `dict[str, str]` также сохраняются в HTTP-ответе.

## Публикация события

```python
from django_event_bus.client import get_event_bus
from users.events import UserCreated

event_bus = get_event_bus()
event_bus.publish(UserCreated(user_id=123, email='user@example.com'))
```

## Запуск consumer

```bash
python manage.py run_event_consumer
```

## Пример и тесты

```bash
pip install -r example/requirements.txt
pytest
```

Опубликовать демонстрационное событие:

```bash
python example/manage.py publish_user_created \
  --user-id 123 \
  --email user@example.com
```
