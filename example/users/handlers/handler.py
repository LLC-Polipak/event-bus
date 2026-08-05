from typing import Any


def handle_example(message: dict[str, Any]) -> None:
    """
    Обработчик события создания контрольного образца.

    Ожидает событие:
    - source: источник (например pro2_dev)
    - payload: данные образца

    Делает:
    - обогащает payload метаданными (creator)
    - создаёт ControlSample
    - применяет дефолтные действия
    """
    try:
        payload = message.get('payload') or {}
        
        if not payload:
            raise ValueError('Empty payload')
        
        print(payload)
        
    
    except Exception as e:
        print('ERROR processing ControlSample.create:', e)
        raise
