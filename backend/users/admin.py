from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'count_subs', 'count_recipes')
    search_fields = ('username', 'email')

    @admin.display(description='Подписчики')
    def count_subs(self, obj):
        return obj.followers.count()

    @admin.display(description='Рецепты')
    def count_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
