from rest_framework.routers import DefaultRouter
from accounts.views import ProfileViewSet
from diary.views import DailySummaryViewSet,MealViewSet,MealItemViewSet
from products.views import CategoryViewSet, ProductViewSet

api_router = DefaultRouter()
api_router.register('profile', ProfileViewSet, basename='profile')
api_router.register('category', CategoryViewSet, basename='category')
api_router.register('products', ProductViewSet, basename='product')
api_router.register('meals', MealViewSet, basename='meal')
api_router.register('meal-items', MealItemViewSet, basename='meal-item')
api_router.register('summary', DailySummaryViewSet, basename='diary-summary')

