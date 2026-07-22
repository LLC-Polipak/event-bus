from dataclasses import dataclass


@dataclass
class EventBusConfig:
    host: str
    port: int
    user: str
    password: str
    vhost: str
    service_name: str
    exchange: str = 'events'
    exchange_type: str = 'topic'
    consumers: list[dict] = list
