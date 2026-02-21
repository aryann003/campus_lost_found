from rest_framework import serializers
from django.contrib.auth import get_user_model

from items.models import Item, Category

User = get_user_model()
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']


class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    owner = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Item 
        fields = ['id', 'title', 'description', 'category', 'category_id', 'type', 'image', 'location', 'date', 'status', 'owner']
