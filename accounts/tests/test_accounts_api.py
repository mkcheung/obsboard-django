from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
REGISTER_URL = reverse('accounts:register')

class PublicAuthApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user(self):
        payload = {
            "name": "Test",
            "email": "testing123@example.com",
            "password": "testing123",
            "password_confirm": "testing123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload['email'])
        self.assertEqual(user.name, payload['name'])
        self.assertTrue(user.check_password(payload["password"]))