from django.utils import timezone
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, viewsets, request
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Meal, MealItem
from .serializers import MealItemSerializer, MealSerializer


# Валидация query-параметров

class MealFilter(filters.FilterSet):
    date = filters.DateFilter()
    profile = filters.NumberFilter(field_name='profile_id')

    class Meta:
        model = Meal
        fields = ['date', 'profile']


class MealItemFilter(filters.FilterSet):
    meal = filters.NumberFilter(field_name='meal_id')

    class Meta:
        model = MealItem
        fields = ['meal']


class SummaryQuerySerializer(serializers.Serializer):
    date = serializers.DateField(required=False)


# Управление приемами пищи. CRUD приемов пищи.
class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer
    queryset = Meal.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = MealFilter

    def get_queryset(self):
        qs = Meal.objects.select_related('profile').prefetch_related('items__product')
        return qs.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


# Управление конкретными строчками еды. Добавлять в готовый прием пищи, изменять вес.
class MealItemViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemSerializer
    queryset = MealItem.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = MealItemFilter

    def get_queryset(self):
        qs = MealItem.objects.select_related('product', 'meal').all()
        return qs.filter(meal__profile__user=self.request.user)

    def perform_create(self, serializer):
        meal = serializer.validated_data['meal']
        if meal.profile.user != self.request.user:
            raise ValidationError({'meal': 'Нельзя добавить в чужой прием пищи'})
        serializer.save()


# Аналитика дневника. Расчет калорий - выдача отчета.
class DailySummaryViewSet(viewsets.ViewSet):

    def list(self, request):
        params = SummaryQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        profile = request.user.profile
        target_date = params.validated_data.get('date') or timezone.localdate()

        meals = Meal.objects.filter(profile=profile, date=target_date).prefetch_related('items')

        consumed = {
            'calories': 0,
            'proteins': 0,
            'fats': 0,
            'carbs': 0
        }
        meals_data = []

        for meal in meals:
            totals = meal.totals()
            meals_data.append({
                'id': meal.id,
                'meal_type': meal.meal_type,
                'meal_type_display': meal.get_meal_type_display(),
                'total': totals,
            })
            for k in consumed:
                consumed[k] += totals[k]

        consumed = {k: round(v, 1) for k, v in consumed.items()}

        targets = profile.calculate_daily_targets() or {}

        remaining = {}
        for k in consumed:
            if targets.get(k) is not None:
                remaining[k] = round(targets[k] - consumed[k], 1)

        return Response({
            'date': target_date,
            'profile': {'id': profile.id, 'name': profile.name},
            'meals': meals_data,
            'consumed': consumed,
            'targets': targets,
            'remaining': remaining,
        })
