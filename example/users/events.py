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


@dataclass(frozen=True, slots=True)
class Address:
    """Адрес из профиля пользователя."""

    city: str
    street: str


@dataclass(frozen=True, slots=True)
class NotificationSettings:
    """Каналы уведомлений, выбранные пользователем."""

    email: bool
    sms: bool


@dataclass(frozen=True, slots=True)
class UserProfile:
    """Вложеные данные профиля пользователя."""

    name: str
    address: Address
    notifications: NotificationSettings
    roles: list[str]


@event(
    code='user.profile.updated',
    title='Профиль пользователя обновлён',
)
@dataclass(frozen=True, slots=True)
class UserProfileUpdated:
    """Событие с вложенным объектом профиля и произвольными метаданными."""

    event_name: ClassVar[str] = 'user.profile.updated'

    user_id: int
    profile: UserProfile
    metadata: dict[str, str]

    def payload(self) -> dict:
        """Преобразовать вложенные dataclass-объекты в словари."""
        return asdict(self)
