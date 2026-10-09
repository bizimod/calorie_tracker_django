from django.contrib import admin
from .models import Category,Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','brand','category',
                    'calories','proteins','fats','carbs')
    list_filter = ('category',)
    search_fields = ('name','brand','category','barcode')
    autocomplete_fields = ('category',)
    ordering = ('-created_at',)