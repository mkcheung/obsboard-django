from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()
CREATE_PROJECT_URL = reverse("projects:projects-list")


def create_user(**params):
    defaults = {
        "name": "Test Name",
        "email": "test@example.com",
        "username": "test@example.com",
        "password": "testpass123",
    }
    defaults.update(params)

    password = defaults.pop("password")
    user = User.objects.create_user(**defaults)
    user.set_password(password)
    user.save()
    return user


class PrivateAuthApiTests(APITestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = create_user(password=self.password)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        payload = {
            "name": "Test",
            "description": "testing123testing123testing123testing123testing123",
        }
        res = self.client.post(CREATE_PROJECT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
