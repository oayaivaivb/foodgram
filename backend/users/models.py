from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (EMAIL_NAME_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
                                LAST_NAME_MAX_LENGTH)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email."""

    email = models.EmailField(unique=True, max_length=EMAIL_NAME_MAX_LENGTH)
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True,
                               null=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки одного пользователя на другого."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription'),
            models.CheckConstraint(condition=~models.Q(
                user=models.F('author')),
                name='no_sefl_subscription')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
