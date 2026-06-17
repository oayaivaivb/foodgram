from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, FavoriteCreateSerializer,
                             FavoriteDeleteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeReadSerializer,
                             RecipeShortSerializer,
                             ShoppingCartCreateSerializer,
                             ShoppingCartDeleteSerializer,
                             SubscriptionCreateSerializer,
                             SubscriptionDeleteSerializer,
                             SubscriptionReadSerializer, TagSerializer,
                             UserSerializer)
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgramPagination

    @action(detail=False, methods=['put', 'delete'],
            url_path='me/avatar', permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'detail': 'Аватар не установлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
    # @action(detail=False, methods=['put',],
    #         url_path='me/avatar', permission_classes=[IsAuthenticated])
    # def set_avatar(self, request):
    #     user = request.user
    #     serializer = AvatarSerializer(user, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['delete',],
    #         url_path='me/avatar', permission_classes=[IsAuthenticated])
    # def delete_avatar(self, request):
    #     user = request.user
    #     if not user.avatar:
    #         return Response(
    #             {'detail': 'Аватар не установлен.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     user.avatar.delete(save=False)
    #     user.avatar = None
    #     user.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionReadSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            url_path='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(data={
                'user': user.id,
                'author': author.id
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = SubscriptionReadSerializer(
                author, context={'request': request}
            )
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            delete_serializer = SubscriptionDeleteSerializer(data={
                'user': user.id,
                'author': author.id
            })
            delete_serializer.is_valid(raise_exception=True)
            deleted_count, _ = Subscription.objects.filter(
                user=user, author=author
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'detail': 'Вы не подписаны.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = FoodgramPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        base_url = request.build_absolute_uri('/')[:-1]
        return Response(
            {'short-link': f"{base_url}/s/{recipe.id}"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post',],
            url_path='favorite', permission_classes=[IsAuthenticated])
    def set_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        serializer = FavoriteCreateSerializer(data={
            'recipe': recipe.id,
            'user': user.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = RecipeShortSerializer(
            recipe, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete',],
            url_path='favorite', permission_classes=[IsAuthenticated])
    def delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        delete_serializer = FavoriteDeleteSerializer(data={
            'recipe': recipe.id,
            'user': user.id
        })
        delete_serializer.is_valid(raise_exception=True)
        deleted_count, _ = Favorite.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if deleted_count == 0:
            return Response(
                {'detail': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post',],
            url_path='shopping_cart', permission_classes=[IsAuthenticated])
    def set_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        serializer = ShoppingCartCreateSerializer(data={
            'recipe': recipe.id,
            'user': user.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = RecipeShortSerializer(
            recipe, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete',],
            url_path='shopping_cart', permission_classes=[IsAuthenticated])
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        delete_serializer = ShoppingCartDeleteSerializer(data={
            'recipe': recipe.id,
            'user': user.id
        })
        delete_serializer.is_valid(raise_exception=True)
        deleted_count, _ = ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if deleted_count == 0:
            return Response(
                {'detail': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user

        if not ShoppingCart.objects.filter(user=user).exists():
            return Response(
                {'detail': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipes__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )

        shopping_list = "Список покупок"
        for item in ingredients:
            shopping_list += (
                f"- {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=utf-8')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


def short_link_redirect(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return redirect(f'/recipes/{recipe.id}/')
