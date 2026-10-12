from django.contrib import admin
from .models import Meal,MealItem

class MealItemAdmin(admin.TabularInline):
    model = MealItem
    extra = 1
    fields = ('product','weight_grams',
              'calories','proteins','fats','carbs')
    readonly_fields = ('calories', 'proteins', 'fats', 'carbs')


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id','profile','date','meal_type')
    list_filter = ('date','meal_type','profile')
    date_hierarchy = 'date'
    autocomplete_fields = ('profile',)
    inlines = [MealItemAdmin]


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ('id','meal','product','weight_grams',
                    'calories','proteins','fats','carbs')
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)
