import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from djoser.serializers import UserSerializer as DjoserUserSerializer

from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)

from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Поле для приёма изображения в формате base64 и преобразования в файл."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели User с добавлением поля is_subscribed."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на данного автора."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепте (по ID)."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя с хешированием пароля."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта (детальный вывод)."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное
        у текущего пользователя."""
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.favorite_user.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок
        у текущего пользователя."""
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.shoppingcart_user.filter(recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Проверяет, что ингредиенты и теги не пустые и не дублируются."""
        ingredients = data.get('ingredients')
        tags = data.get('tags')

        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть как минимум один ингредиент.')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть как минимум один тег.')

        ingredient_ids = [item['id'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.')

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.')

        return data

    def create_ingredients_amounts(self, ingredients, recipe):
        """Создаёт связи рецепта с ингредиентами с указанием количества."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        """Создаёт рецепт с ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags_data)
        self.create_ingredients_amounts(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт, перезаписывая ингредиенты и теги."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients_amounts(ingredients_data, instance)

        return instance

    def to_representation(self, instance):
        """Возвращает данные в формате RecipeReadSerializer."""
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого вывода рецепта (ID, имя, картинка, время)."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Базовый абстрактный сериализатор для избранного и списка покупок."""

    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверяет, не добавлен ли уже рецепт в избранное/список покупок."""
        user = data.get('user')
        recipe = data.get('recipe')
        relation = self.Meta.model.objects.filter(user=user, recipe=recipe)

        if relation.exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')
        return data

    def to_representation(self, instance):
        """Возвращает краткую информацию о рецепте."""
        return RecipeShortSerializer(
            instance.recipe, context=self.context).data


class FavoriteSerializer(BaseFavoriteShoppingCartSerializer):
    """Сериализатор для модели Favorite."""

    class Meta(BaseFavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseFavoriteShoppingCartSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta(BaseFavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart


class SubscriptionReadSerializer(UserSerializer):
    """Сериализатор для отображения подписок с рецептами автора."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        """Возвращает рецепты автора с учётом параметра recipes_limit."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        queryset = obj.recipes.all()
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(
            queryset, many=True, context=self.context
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        """Проверяет, что пользователь не подписывается на себя
        и подписка ещё не существует."""
        user = data.get('user')
        author = data.get('author')
        subscription = Subscription.objects.filter(user=user, author=author)
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        if subscription.exists():
            raise serializers.ValidationError('Вы уже подписаны.')
        return data

    def to_representation(self, instance):
        """Возвращает данные в формате SubscriptionReadSerializer."""
        return SubscriptionReadSerializer(
            instance.author, context=self.context).data
