from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import ProfileViewSet, RegisterView, LogoutView
from diary.views import DailySummaryViewSet, MealViewSet, MealItemViewSet
from products.views import CategoryViewSet, ProductViewSet

from django.urls import path

api_router = DefaultRouter()
api_router.register('profile', ProfileViewSet, basename='profile')
api_router.register('category', CategoryViewSet, basename='category')
api_router.register('products', ProductViewSet, basename='product')
api_router.register('meals', MealViewSet, basename='meal')
api_router.register('meal-items', MealItemViewSet, basename='meal-item')
api_router.register('summary', DailySummaryViewSet, basename='diary-summary')

auth_urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]

urlpatterns = auth_urlpatterns + api_router.urls