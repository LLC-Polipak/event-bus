from django.utils.module_loading import import_string

from django_event_bus.client import get_event_bus


def start_consumer():
    bus = get_event_bus()

    for consumer in bus.config.consumers:
        if not consumer.get('enabled', True):
            print(f'skip disabled consumer {consumer}')
            continue

        print(f'registering consumer {consumer}')
        handler = import_string(consumer['handler'])
        bus.subscribe(
            consumer['source'],
            consumer['routing_key'],
            handler,
        )

    bus.run()
