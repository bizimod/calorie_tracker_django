from datetime import date
from unittest import TestCase

from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Profile


class ProfileAPITest(APITestCase):
    def test_create_profile(self):
        url = reverse('profile-list')
        data = {'name': 'Тест', 'gender': 'male',
                'weight': 100, 'height': 200}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.count(), 1)

    def test_create_profile_invalid_data(self):
        url = reverse('profile-list')
        data = {'name': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_create_profile_invalid_gender(self):
        url = reverse('profile-list')
        data = {'name': 'Тест', 'gender': 'wolf'
            , 'weight': 100, 'height': 200}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('gender', response.data)

    def test_get_profile_list(self):
        Profile.objects.create(name='Тест', gender='male'
                               , weight=100, height=200)
        url = reverse('profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_profile_detail(self):
        profile = Profile.objects.create(name='Тест', gender='male'
                                         , weight=100, height=200)
        url = reverse('profile-detail'
                      , kwargs={'pk': profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], profile.name)

class NutritionCalculationTest(TestCase):

    def test_bmr_male(self):
        profile = Profile(weight=80, height=180,gender='male',
                          birth_date = date(2000,1,1))
        bmr = profile.calculate_bmr()
        self.assertAlmostEqual(bmr,1800,places=0)

    def test_bmr_female(self):
        profile = Profile(weight=80, height=180,gender='female',
                          birth_date = date(2000,1,1))
        bmr = profile.calculate_bmr()
        self.assertAlmostEqual(bmr,1634,places=0)

    def test_missing_data_returns_none(self):
        profile = Profile(weight=80)
        self.assertIsNone(profile.calculate_bmr())
        self.assertIsNone(profile.calculate_daily_targets())

    def test_daily_targets(self):
        profile = Profile(weight=80, height=180,gender='male',
                          birth_date = date(2000,1,1),
                          activity = 'moderate',goal='lose')
        result = profile.calculate_daily_targets()
        self.assertIn('calories', result)
        self.assertIn('proteins', result)
        self.assertGreater(result['calories'], 0)
