from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов: поиск по началу названия (без учёта регистра)."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр ингредиентов по началу названия (регистронезависимо)."""

    author = filters.NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов, добавленных в список покупок текущего пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                shoppingcart_recipe__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов, добавленных в избранное текущего пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                favorite_recipe__user=self.request.user)
        return queryset
