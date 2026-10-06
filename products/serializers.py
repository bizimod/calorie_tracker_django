from rest_framework import serializers
from .models import Category,Product

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(
        source='products.count',read_only=True
    )
    class Meta:
        model = Category
        fields = ['id','name','product_count']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',read_only=True
    )
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'category', 'category_name',
            'calories', 'proteins', 'fats', 'carbs',
            'barcode', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id','name','brand','calories']