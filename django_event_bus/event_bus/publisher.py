from .message import build_message, serialize


class Publisher:
    def __init__(self, channel, config):
        self.channel = channel
        self.config = config

        # declare exchange
        self.channel.exchange_declare(
            exchange=self.config.exchange,
            exchange_type='topic',
            durable=True,
        )

    def publish(self, source: str, event: str, payload: dict):
        routing_key = f'{source}.{event}'

        message = build_message(source, event, payload)

        self.channel.basic_publish(
            exchange=self.config.exchange,
            routing_key=routing_key,
            body=serialize(message),
        )
