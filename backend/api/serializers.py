import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from backend.users.models import User
from backend.recipes.models import Recipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'avatar']
    



class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'ingredients', 'instructions']

class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity = serializers.CharField(max_length=100)

class TagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)

class 
