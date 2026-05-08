from django.conf import settings
from django.utils.module_loading import import_string

from django_event_bus import EventBus, EventBusConfig


def start_consumer():
    cfg = settings.EVENT_BUS

    config = EventBusConfig(
        host=cfg['HOST'],
        port=cfg['PORT'],
        user=cfg['USER'],
        password=cfg['PASSWORD'],
        vhost=cfg['VHOST'],
        service_name=cfg['SERVICE_NAME'],
        exchange=cfg['EXCHANGE'],
    )

    bus = EventBus(config)

    for consumer in cfg.get('CONSUMERS', []):
        handler = import_string(consumer['handler'])

        bus.subscribe(
            consumer['source'],
            consumer['routing_key'],
            handler,
        )

    bus.run()
