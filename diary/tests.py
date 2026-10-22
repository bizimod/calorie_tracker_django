from datetime import date
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from products.models import Product
from .models import Meal, MealItem

from django.contrib.auth import get_user_model
from config.test_utils import AuthenticatedAPITestCase

User = get_user_model()


class DiaryTest(AuthenticatedAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', username='test', password='pass123'
        )
        self.client.force_authenticate(user=self.user)

        # профиль создался автоматически сигналом
        self.profile = self.user.profile
        self.profile.weight = 80
        self.profile.height = 180
        self.profile.birth_date = date(2000, 1, 1)
        self.profile.gender = 'male'
        self.profile.activity = 'moderate'
        self.profile.goal = 'maintain'
        self.profile.save()

        self.product = Product.objects.create(
            name='Гречка', calories=343, proteins=12.6,
            fats=3.3, carbs=62.1,
        )

    def test_meal_item_calculates_macros(self):
        meal = Meal.objects.create(
            profile=self.profile, date=date.today(), meal_type='breakfast',
        )
        item = MealItem.objects.create(
            meal=meal, product=self.product, weight_grams=150
        )
        self.assertEqual(item.calories, 514.5)
        self.assertEqual(item.proteins, 18.9)

    def test_meal_item_recalculate_on_weight_change(self):
        meal = Meal.objects.create(
            profile=self.profile, date=date.today(), meal_type='breakfast',
        )
        item = MealItem.objects.create(
            meal=meal, product=self.product, weight_grams=100
        )
        self.assertEqual(item.calories, 343)

        item.weight_grams = 200
        item.save()
        item.refresh_from_db()
        self.assertEqual(item.calories, 686)

    def test_daily_meal(self):
        meal = Meal.objects.create(
            profile=self.profile, date=timezone.localdate(), meal_type='breakfast',
        )
        MealItem.objects.create(meal=meal, product=self.product, weight_grams=100)

        response = self.client.get(reverse('diary-summary-list'), {
            'date': timezone.localdate().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['consumed']['calories'], 343)

    def test_summary_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('diary-summary-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_meal_for_other_profile(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass12345'
        )
        response = self.client.post(reverse('meal-list'), {
            'profile': other.profile.id,
            'date': timezone.localdate().isoformat(),
            'meal_type': 'lunch',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['profile'], self.profile.id)   # подменился на свой

    def test_cannot_move_item_to_other_meal(self):
        other = User.objects.create_user(
            email='other@example.com', username='other_m', password='pass12345'
        )
        other_meal = Meal.objects.create(
            profile=other.profile, date=timezone.localdate(), meal_type='lunch',
        )
        my_meal = Meal.objects.create(
            profile=self.profile, date=timezone.localdate(), meal_type='breakfast',
        )
        item = MealItem.objects.create(
            meal=my_meal, product=self.product, weight_grams=100,
        )

        response = self.client.patch(
            reverse('meal-item-detail', kwargs={'pk': item.pk}),
            {'meal': other_meal.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # позиция осталась в моём meal
        item.refresh_from_db()
        self.assertEqual(item.meal_id, my_meal.id)