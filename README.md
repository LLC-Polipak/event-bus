# Django Event Bus

Reusable event bus based on RabbitMQ for Django projects.

## Installation

```bash
pip install event_bus git+https://github.com/LLC-Polipak/event-bus.git   
 #TODO pip install event-bus
```

### Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'django_event_bus',
]
```
### Required settings

```python
EVENT_BUS = {
    'HOST': 'localhost',
    'PORT': 5672,
    'USER': 'guest',
    'PASSWORD': 'guest',
    'VHOST': '/',
    'SERVICE_NAME': 'my_service',
    'EXCHANGE': 'events',  # optional, default: 'events'
    
    'CONSUMERS': [
        {
            'source': 'order_service',
            'routing_key': 'order.created',
            'handler': 'myapp.handlers.handle_order_created',
        },
    ],
}
```

## Usage

### Publishing events
```python

from django_event_bus.client import get_event_bus


bus = get_event_bus()

bus.publish('user.registered', {
    'user_id': 123,
    'email': 'user@example.com'
})
```
## Running consumer
```bash
python manage.py run_event_consumer
```
