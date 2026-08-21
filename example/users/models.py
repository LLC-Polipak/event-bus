"""Модели пользователей демонстрационного Django-приложения."""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Пользователь примера на основе стандартной Django-модели."""
