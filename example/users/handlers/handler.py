"""Обработка входящих событий в демонстрационном users-приложении."""

from typing import Any


def handle_example(message: dict[str, Any]) -> None:
    """Проверить и вывести payload демонстрационного события.

    Args:
        message: Десериализованное сообщение event bus с обязательным payload.

    Raises:
        ValueError: Payload отсутствует или пуст.
    """
    try:
        payload = message.get('payload') or {}

        if not payload:
            raise ValueError('Empty payload')

        print(payload)

    except Exception as e:
        print('ERROR processing ControlSample.create:', e)
        raise
