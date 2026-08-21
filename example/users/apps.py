"""Конфигурация Django-приложения users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Подключает приложение users и регистрирует его события."""

    name = 'users'

    def ready(self) -> None:
        """Импортирует модуль, чтобы декораторы зарегистрировали события."""
        from users import events  # noqa: F401
