from .message import deserialize


class Consumer:
    def __init__(self, channel, config):
        self.channel = channel
        self.config = config
        self.subscriptions = []

        self.channel.exchange_declare(
            exchange=self.config.exchange,
            exchange_type='topic',
            durable=True,
        )

    def subscribe(self, source: str, event: str, handler):
        routing_key = f'{source}.{event}'
        queue_name = f'{self.config.service_name}.{source}.{event}'

        # declare queue
        self.channel.queue_declare(queue=queue_name, durable=True)

        # bind
        self.channel.queue_bind(
            exchange=self.config.exchange,
            queue=queue_name,
            routing_key=routing_key,
        )

        self.subscriptions.append((queue_name, handler))

    def start(self):
        for queue_name, handler in self.subscriptions:

            def make_callback(handler):
                def callback(ch, method, _properties, body):
                    try:
                        message = deserialize(body)
                    except Exception as e:
                        print(f'Deserialize error: {e}')
                        print(f'RAW: {body}')

                        # 💥 съедаем битое сообщение
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return

                    try:
                        handler(message)
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                    except Exception as e:
                        print(f'Handler error: {e}')
                        # сейчас у тебя бесконечный retry
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        # если поставить True → цикл

                return callback

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=make_callback(handler),
            )

        print(' [*] Waiting for messages...')
        self.channel.start_consuming()
