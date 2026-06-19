from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from foodgram.constants import (INGREDIENT_NAME_MAX_LENGTH, NAME_MAX_LENGTH,
                                TIME_AMOUT_MIN_VALUE)


class Ingredient(models.Model):
    name = models.CharField(unique=True, max_length=NAME_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient_unit')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient',
                                         related_name='recipes')
    tags = models.ManyToManyField('Tag', related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(TIME_AMOUT_MIN_VALUE)])
    pub_date = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE,
                                   related_name='recipe_ingredients')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(TIME_AMOUT_MIN_VALUE)])

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe_ingredient')
        ]


class ShoppingFavoriteBaseModel(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='%(class)s_user'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='%(app_label)s_%(class)s_unique')
        ]


class Favorite(ShoppingFavoriteBaseModel):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(ShoppingFavoriteBaseModel):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
