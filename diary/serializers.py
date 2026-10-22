from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from products.serializers import ProductShortSerializer
from .models import Meal, MealItem


class MealItemSerializer(serializers.ModelSerializer):
    product_detail = ProductShortSerializer(source='product', read_only=True)

    class Meta:
        model = MealItem
        fields = [
            'id', 'meal', 'product', 'product_detail', 'weight_grams',
            'calories', 'proteins', 'fats', 'carbs', 'created_at',
        ]
        read_only_fields = ['id', 'calories', 'proteins', 'fats', 'carbs', 'created_at']


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    totals = serializers.SerializerMethodField()
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)

    class Meta:
        model = Meal
        fields = [
            'id', 'profile', 'date', 'meal_type', 'meal_type_display',
            'items', 'totals', 'created_at',
        ]
        read_only_fields = ['id', 'profile', 'created_at']

    def get_totals(self, obj):
        return obj.totals()

