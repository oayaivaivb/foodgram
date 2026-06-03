from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # username = models.CharField(unique=True, max_length=150)
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=160)
    last_name = models.CharField(max_length=150)
    # password = models.CharField(max_length=128)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_subscription')
        ]
