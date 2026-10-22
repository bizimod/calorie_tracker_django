from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            email='test@example.com', username='test', password='pass12345'
        )
        self.client.force_authenticate(user=self.user)
        self.profile = self.user.profile