"""Примеры событий приложения users."""

from dataclasses import asdict, dataclass
from typing import ClassVar

from django_event_bus.event_bus.events import event


@event(
    code='user.created',
    title='Пользователь создан',
)
@dataclass(frozen=True, slots=True)
class UserCreated:
    """Событие, публикуемое после создания пользователя."""

    event_name: ClassVar[str] = 'user.created'

    user_id: int
    email: str

    def payload(self) -> dict:
        """Возвращает данные для публикации в event bus."""
        return asdict(self)
