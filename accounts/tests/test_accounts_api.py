from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
REGISTER_URL = reverse('accounts:register')
LOGIN_URL = reverse('accounts:login')

User = get_user_model()

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

    def test_register_creates_user_missing_name(self):
        payload = {
            "name": "",
            "email": "testing123@example.com",
            "password": "testing123",
            "password_confirm": "testing123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user_missing_email(self):
        payload = {
            "name": "Test",
            "email": "",
            "password": "testing123",
            "password_confirm": "testing123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user_missing_password(self):
        payload = {
            "name": "Test",
            "email": "testing123@example.com",
            "password": "",
            "password_confirm": "testing123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_user_missing_password_confirm(self):
        payload = {
            "name": "Test",
            "email": "testing123@example.com",
            "password": "testing123",
            "password_confirm": "",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        register_payload = {
            'email': 'test@example.com',
            'username': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(REGISTER_URL, register_payload, format="json")
        payload = {
            'email': register_payload['email'],
            'password': register_payload['password']
        }
        res = self.client.post(LOGIN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_incorrect_password(self):
        register_payload = {
            'email': 'test@example.com',
            'username': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(REGISTER_URL, register_payload, format="json")
        payload = {
            'email': register_payload['email'],
            'password': 'testpas'
        }
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_email(self):
        register_payload = {
            'email': 'test@example.com',
            'username': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(REGISTER_URL, register_payload, format="json")
        payload = {
            'email': '',
            'password': 'testpass123'
        }
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
