from django.urls import path

from . import views

app_name = 'web'

urlpatterns = [
    path('', views.day_today, name='today'),
    path('day/<str:date>/', views.day_view, name='day'),
    path('day/<str:date>/meal/<str:meal_type>/add/', views.create_meal, name='create-meal'),
    path('meals/<int:meal_id>/items/<int:pk>/add/', views.add_product_to_meal, name='add-product'),
    path('items/<int:pk>/delete/', views.delete_item, name='delete-item'),
    path('products/search/', views.product_search, name='product-search'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
]