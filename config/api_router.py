from rest_framework.routers import DefaultRouter
from accounts.views import ProfileViewSet
from products.views import CategoryViewSet, ProductViewSet

api_router = DefaultRouter()
api_router.register('profile', ProfileViewSet, basename='profile')
api_router.register('category', CategoryViewSet, basename='category')
api_router.register('products', ProductViewSet, basename='products')

