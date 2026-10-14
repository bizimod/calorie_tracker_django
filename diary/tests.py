from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from accounts.models import Profile
from products.models import Product
from .models import Meal, MealItem


class DiaryTest(APITestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            name='Тест', weight=80, height=180,
            birth_date=date(2000, 1, 1), gender='male',
            activity='moderate', goal='maintain'
        )
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