"""Запуск обработчиков событий, описанных в Django settings."""

import logging
import signal
import threading

from django.utils.module_loading import import_string

from django_event_bus.client import get_event_bus
from django_event_bus.settings import get_consumer_selection, get_event_bus_config

logger = logging.getLogger(__name__)


def wait_until_stopped():
    """Wait without polling until SIGTERM or SIGINT is received."""
    stop_event = threading.Event()

    def stop(_signum, _frame):
        stop_event.set()

    previous_handlers = {
        signum: signal.signal(signum, stop)
        for signum in (signal.SIGTERM, signal.SIGINT)
    }
    try:
        stop_event.wait()
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


def start_consumer():
    """Подписать включённые обработчики и запустить consumer."""
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError('Event bus consumer must run in the main thread')

    config = get_event_bus_config()
    consumers = get_consumer_selection(config)

    if not consumers.globally_enabled:
        logger.info('Event bus consumer is disabled')
        wait_until_stopped()
        return

    for consumer in consumers.disabled:
        logger.info(
            'Skipping disabled event consumer: %s',
            consumer.get('handler', '<unspecified>'),
        )

    if not consumers.enabled:
        logger.info('No enabled event bus consumers are configured')
        wait_until_stopped()
        return

    logger.info(
        'Starting event bus consumer with %d subscription(s)',
        len(consumers.enabled),
    )
    bus = get_event_bus()

    for consumer in consumers.enabled:
        handler = import_string(consumer['handler'])
        bus.subscribe(
            consumer['source'],
            consumer['routing_key'],
            handler,
        )

    bus.run()
