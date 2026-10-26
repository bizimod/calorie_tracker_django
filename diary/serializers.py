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
        items = list(obj.items.all())
        return {
            k: round(sum(getattr(i, k) for i in items), 1)
            for k in ('calories', 'proteins', 'fats', 'carbs')
        }

    # Обработчик добавления повторного приема пищи который уже был добавлен
    def validate(self, attrs):
        profile = self.instance.profile if self.instance else self.context['request'].user.profile
        date = attrs.get('date', getattr(self.instance, 'date', None))
        meal_type = attrs.get('meal_type', getattr(self.instance, 'meal_type', None))
        qs = Meal.objects.filter(profile=profile, date=date, meal_type=meal_type)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({'meal_type': 'Прием пищи этого типа на эту дату уже существует'})
        return attrs
