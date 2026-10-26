"""from rest_framework.routers import DefaultRouter
from .views import MealViewSet, MealItemViewSet, DailySummaryViewSet

router = DefaultRouter()
router.register('meals', MealViewSet, basename='meal')
router.register('meal-items', MealItemViewSet, basename='meal-item')
router.register('diary/summary', DailySummaryViewSet, basename='diary-summary')

urlpatterns = router.urls"""