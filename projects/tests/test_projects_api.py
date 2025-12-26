from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import (
    Project,
)

User = get_user_model()
PROJECT_URL = reverse("projects:projects-list")


def detail_url(project_id):
    return reverse("projects:projects-detail", args=[project_id])


def create_user(**params):
    defaults = {
        "name": "Test Name",
        "email": "test@example.com",
        "password": "testpass123",
    }
    defaults.update(params)
    # Ensure username is unique
    if "username" not in defaults:
        defaults["username"] = defaults["email"]
    password = defaults.pop("password")
    user = User.objects.create_user(**defaults)
    user.set_password(password)
    user.save()
    return user


def create_project(user, **params):
    defaults = {
        "name": "TestDefault",
        "description": "Default",
    }
    defaults.update(params)
    project = Project.objects.create(user=user, **defaults)
    return project


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
        res = self.client.post(PROJECT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_find_nonexistent_project(self):
        url = detail_url(999999)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_find_project_with_term(self):
        project1 = create_project(
            user=self.user, name="Project 1 target", description="None"
        )
        project2 = create_project(
            user=self.user,
            name="Project 2",
            description="This contains a target to find",
        )
        project3 = create_project(user=self.user, name="P3", description="P3")
        res = self.client.get(
            f"{PROJECT_URL}?search=target&sort=created_at&dir=desc&page_size=10"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data.get("data", res.data))
        self.assertEqual(2, len(results))
        project_ids_created_order = [project["id"] for project in results]
        self.assertEqual(
            project_ids_created_order, [results[0]["id"], results[1]["id"]]
        )
        self.assertEqual(project2.name, results[0]["name"])
        self.assertEqual(project2.description, results[0]["description"])
        self.assertEqual(project1.name, results[1]["name"])
        self.assertEqual(project1.description, results[1]["description"])

    def test_update_project_partial(self):
        project = create_project(
            user=self.user,
        )

        payload = {"description": "testingUpdated"}
        url = detail_url(project.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.name, "TestDefault")
        self.assertEqual(project.description, "testingUpdated")

    def test_update_another_users_project(self):
        other_user = create_user(email="test999@example.com")
        project = create_project(
            user=other_user,
        )

        payload = {"description": "testingUpdated"}
        url = detail_url(project.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_project_full(self):
        project = create_project(
            user=self.user,
        )

        payload = {
            "name": "Test Full Update",
            "description": "New project description",
        }
        url = detail_url(project.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(project, key), value)

    def test_delete_project(self):
        project = create_project(
            user=self.user,
        )
        url = detail_url(project.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project.id).exists())
