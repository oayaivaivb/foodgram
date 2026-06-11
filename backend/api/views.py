from djoser.views import UserViewSet as DjoserUserViewSet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .serializers import IngredientSerializer, RecipeCreateSerializer, RecipeSerializer, RecipeShortSerializer, TagSerializer, UserSerializer, UserCreateSerializer, UserWithRecipesSerializer, AvatarSerializer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from users.models import User


class FoodgramPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = 6


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = FoodgramPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateSerializer

    def _handle_relation(self, request, model, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.metod == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже добавлен.'}, status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.metod == 'DELETE':
            relation = model.objects.filter(user=user, recipe=recipe)
            if not relation.exists():
                return Response({'detail': 'Рецепт не найден в списке.'}, status=status.HTTP_400_BAD_REQUEST)
            relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._handle_relation(request, Favorite, pk)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._handle_relation(request, ShoppingCart, pk)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        if not shopping_cart_items.exists():
            return Response({'detail': 'Список покупок пуст.'}, status=status.HTTP_400_BAD_REQUEST)

        ingredients = {}
        for item in shopping_cart_items:
            recipe_ingredients = item.recipe.recipeingredient_set.all()
            for ri in recipe_ingredients:
                ingredient_name = ri.ingredient.name
                measurement_unit = ri.ingredient.measurement_unit
                amount = ri.amount
                if ingredient_name in ingredients:
                    ingredients[ingredient_name]['amount'] += amount
                else:
                    ingredients[ingredient_name] = {'amount': amount, 'measurement_unit': measurement_unit}

        shopping_list = 'Список покупок:\n\n'
        for name, details in ingredients.items():
            shopping_list += f"{name}: {details['amount']} {details['measurement_unit']}\n"

        response = HttpResponse(shopping_list, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class UserViewSet(DjoserUserViewSet):
    pagination_class = FoodgramPagination

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if author == user:
            return Response({'detail': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)

        subscription = user.follower.filter(author=author)

        if request.method == 'POST':
            if subscription.exist():
                return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
            user.follower.create(author=author)
            serializer = UserWithRecipesSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exist():
                return Response({'detail': 'Вы не подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar', permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
  
