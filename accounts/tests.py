from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile

User = get_user_model()


class ProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', username='test', password='pass12345'
        )
        self.client.force_authenticate(user=self.user)
        self.profile = self.user.profile

    def test_profile_created_by_signal(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_me_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get(self):
        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_me_patch(self):
        response = self.client.patch(
            reverse('profile-me'), {'weight': 100, 'height': 200}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], 100)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.weight, 100)

    def test_put_invalid_gender(self):
        response = self.client.put(
            reverse('profile-me'), {'gender': 'wolf'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data)

    def test_me_invalid_gender(self):
        response = self.client.patch(reverse('profile-me'), {'gender': 'wolf'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data)

    def test_me_shows_only_own_profile(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass12345'
        )
        other.profile.weight = 55
        other.profile.save()

        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.data['weight'], self.profile.weight)


class RegisterAPITest(APITestCase):
    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'username': 'new',
            'password': 'StrongPass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='new@example.com')
        self.assertTrue(user.check_password('StrongPass123'))  # ловит баг с открытым паролем
        self.assertTrue(hasattr(user, 'profile'))  # ловит отсутствие сигнала

    def test_register_duplicate_email(self):
        User.objects.create_user(email='dup@example.com', username='dup', password='pass12345')
        response = self.client.post(reverse('register'), {
            'email': 'dup@example.com', 'username': 'dup2', 'password': 'StrongPass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        response = self.client.post(reverse('register'), {
            'email': 'weak@example.com', 'username': 'weak', 'password': '123456',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_obtain(self):
        User.objects.create_user(email='jwt@example.com', username='jwt', password='StrongPass123')
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'jwt@example.com', 'password': 'StrongPass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
