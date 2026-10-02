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
