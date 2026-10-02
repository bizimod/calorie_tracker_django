from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Profile


class ProfileAPITest(APITestCase):
    def test_create_profile(self):
        url = reverse('profile-list')
        data = {'name': 'Тест','gender':'male',
                'weight': 100,'height':200}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,201)
        self.assertEqual(Profile.objects.count(),1)