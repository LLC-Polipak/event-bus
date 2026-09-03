"""Параметры подключения event bus к RabbitMQ и описания consumer."""

from dataclasses import dataclass, field


@dataclass
class EventBusConfig:
    """Конфигурация RabbitMQ-транспорта и подписок event bus."""

    host: str
    port: int
    user: str
    password: str
    vhost: str
    service_name: str
    exchange: str = 'events'
    exchange_type: str = 'topic'
    consumers: list[dict] = field(default_factory=list)
