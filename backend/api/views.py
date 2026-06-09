from django.shortcuts import render

from backend.users.models import User
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from backend.api.serializers import IngredientSerializer, RecipeCreateSerializer, RecipeSerializer, RecipeShortSerializer, TagSerializer, UserSerializer, UserCreateSerializer, UserWithRecipesSerializer
from backend.recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST' and Favorite.objects.filter(user=request.user, recipe_id=pk).exists():
            return Response({'detail': 'Рецепт уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'POST':
            Favorite.objects.create(user=request.user, recipe_id=pk)
            recipe = Recipe.objects.get(pk=pk)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and not Favorite.objects.filter(user=request.user, recipe_id=pk).exists():
            return Response({'detail': 'Рецепт не найден в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            Favorite.objects.filter(user=request.user, recipe_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST' and ShoppingCart.objects.filter(user=request.user, recipe_id=pk).exists():
            return Response({'detail': 'Рецепт уже в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'POST':
            ShoppingCart.objects.create(user=request.user, recipe_id=pk)
            recipe = Recipe.objects.get(pk=pk)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and not ShoppingCart.objects.filter(user=request.user, recipe_id=pk).exists():
            return Response({'detail': 'Рецепт не найден в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(user=request.user, recipe_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewSet):
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
        author = self.get_object()

        if author == user:
            return Response({'detail': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST' and user.follower.filter(author=author).exists():
            return Response({'detail': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'POST':
            user.follower.create(author=author)
            serializer = UserWithRecipesSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and not user.follower.filter(author=author).exists():
            return Response({'detail': 'Вы не подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user.follower.filter(author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
