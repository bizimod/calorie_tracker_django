from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from accounts.models import Profile
from products.models import Product
from .models import Meal, MealItem

from django.contrib.auth import get_user_model
User = get_user_model()

class DiaryTest(APITestCase):
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
        self.profile.activity_level = 'moderate'
        self.profile.goal = 'maintain'
        self.profile.save()

        self.product = Product.objects.create(
            name='Гречка', calories=343, proteins=12.6,
            fats=3.3, carbs=62.1,
        )

    def test_meal_item_calculates_macros(self):
        meal = Meal.objects.create(
            profile=self.profile,date = date.today(),meal_type = 'breakfast',
        )
        item = MealItem.objects.create(
            meal=meal,product=self.product,weight_grams=150
        )
        self.assertEqual(item.calories,514.5)
        self.assertEqual(item.proteins,18.9)

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
            profile=self.profile, date=date.today(), meal_type='breakfast',
        )
        item = MealItem.objects.create(
            meal=meal, product=self.product, weight_grams=100
        )
        url = reverse('diary-summary-list')

        response = self.client.get(url,{
            'profile':self.profile.id,
            'date':date.today().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['consumed']['calories'],343)
        self.assertIn('targets', response.data)
        self.assertIn('remaining', response.data)