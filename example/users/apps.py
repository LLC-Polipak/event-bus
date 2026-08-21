from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self) -> None:
        """Импортирует модуль, чтобы декораторы зарегистрировали события."""
        from users import events  # noqa: F401
