from datetime import date as date_cls

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.models import Profile
from .models import Meal, MealItem
from .serializers import MealSerializer, MealItemSerializer


# управление приемами пищи. CRUD приемов пищи.
class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer

    def get_queryset(self):
        qs = Meal.objects.select_related('profile').prefetch_related('items__product')
        profile_id = self.request.query_params.get('profile')
        date = self.request.query_params.get('date')
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        if date:
            qs = qs.filter(date=date)
        return qs

# Управление конкретными строчками еды. Добавлять в готовый прием пищи, изменять вес.
class MealItemViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemSerializer
    queryset = MealItem.objects.select_related('product','meal').all()

    def get_queryset(self):
        qs = super().get_queryset()
        meal_id = self.request.query_params.get('meal')
        if meal_id:
            qs = qs.filter(meal_id=meal_id)
        return qs

# Аналитика дневника. Рассчет калорий - выдача отчета.
class DailySummaryViewSet(viewsets.ViewSet):

    def list(self, request):
        profile_id = request.query_params.get('profile')
        date_str = request.query_params.get('date')

        if not profile_id:
            return Response({'detail':'Параметр profile обязателен'},
                            status=status.HTTP_400_BAD_REQUEST)
        profile = get_object_or_404(Profile, id=profile_id)
        target_date = (date_cls.fromisoformat(date_str) if date_str else date_cls.today())
        meals = Meal.objects.filter(profile=profile,date=target_date).prefetch_related('items')

        consumed = {
            'calories':0,
            'proteins':0,
            'fats':0,
            'carbs':0
        }
        meals_data = []

        for meal in meals:
            totals = meal.totals()
            meals_data.append({
                'id':meal.id,
                'meal_type':meal.meal_type,
                'meal_type_display':meal.get_meal_type_display(),
                'total':totals,
            })
            for k in consumed:
                consumed[k] += totals[k]

        consumed = {k:round(v,1) for k,v in consumed.items()}

        targets = profile.calculate_daily_targets() or {}

        remaining = {}
        for k in consumed:
            if targets.get(k) is not None:
                remaining[k] = round(targets[k] - consumed[k],1)

        return Response({
            'date':target_date,
            'profile':{'id':profile.id,'name':profile.name},
            'meals':meals_data,
            'consumed':consumed,
            'targets':targets,
            'remaining':remaining,
        })