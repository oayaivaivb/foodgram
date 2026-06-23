from django.contrib import admin
from django.utils.html import format_html

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка отображения модели Tag в админке."""

    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели Tag в админке."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Inline-форма для управления ингредиентами внутри рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения модели Recipe в админке."""

    list_display = ('name', 'author', 'cooking_time',
                    'in_is_favorite', 'image_preview')
    list_filter = ('author', 'tags')
    search_fields = ('author__username', 'name')
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Добавлений в избранное')
    def in_is_favorite(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return obj.favorite_recipe.count()

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        """Возвращает HTML-код для превью изображения рецепта."""
        return format_html('<img src="{}" width="50" height="50">',
                           obj.image.url)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели RecipeIngredient в админке."""

    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка отображения модели Favorite в админке."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка отображения модели ShoppingCart в админке."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)
