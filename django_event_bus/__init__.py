"""
Django Event Bus - переиспользуемая событийная шина на RabbitMQ
"""

__version__ = '0.1.0'

__all__ = ['EventBus', 'EventBusConfig', 'Consumer', 'start_consumer', 'Publisher']

from django_event_bus.consumer import start_consumer
from django_event_bus.event_bus.bus import EventBus
from django_event_bus.event_bus.config import EventBusConfig
from django_event_bus.event_bus.consumer import Consumer
from django_event_bus.event_bus.publisher import Publisher
