from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import (
    Task,
)

from projects.models import (
    Project,
)

User = get_user_model()
TASK_URL = reverse("tasks:tasks-list")


def default_url(task_id):
    return reverse("tasks:tasks-detail", args=[task_id])


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


def create_project(user, **params):
    defaults = {
        "name": "TestDefault",
        "description": "Default",
    }
    defaults.update(params)
    project = Project.objects.create(user=user, **defaults)
    return project


def create_task(user, project_id, **params):
    defaults = {
        "project_id": project_id,
        "title": "create task unit test",
        "description": "testing basic crud - create",
        "status": "doing",
        "priority": "high",
        "due_date": "2025-01-15",
        "estimate_minutes": 90,
    }
    defaults.update(params)
    task = Task.objects.create(user=user, **defaults)
    return task


class PrivateAuthApiTests(APITestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = create_user(password=self.password)
        self.project = create_project(user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        payload = {
            "project_id": self.project.id,
            "title": "create task unit test",
            "description": "testing basic crud - create",
            "status": "doing",
            "priority": "high",
            "due_date": "2025-01-15",
            "estimate_minutes": 90,
        }
        res = self.client.post(TASK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_by_priority(self):
        task1 = create_task(
            user=self.user,
            project_id=self.project.id,
            priority="high",
            due_date=date(2025, 1, 5),
        )
        task2 = create_task(
            user=self.user,
            project_id=self.project.id,
            priority="high",
            due_date=date(2025, 1, 3),
        )
        task3 = create_task(
            user=self.user,
            project_id=self.project.id,
            priority="low",
            due_date=date(2025, 1, 6),
        )
        res = self.client.get(f"{TASK_URL}?priority=low&page_size=10")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data.get("data", res.data))
        self.assertEqual(1, len(results))
        result_content = results[0]
        self.assertEqual(result_content["id"], task3.id)
        self.assertEqual(result_content["priority"], task3.priority)
        self.assertEqual(result_content["project_id"], task3.project.id)
        self.assertEqual(
            result_content["due_date"], task3.due_date.strftime("%Y-%m-%d")
        )

    def test_filter_by_status(self):
        task1 = create_task(user=self.user, project_id=self.project.id, status="todo")

        task2 = create_task(user=self.user, project_id=self.project.id, status="doing")

        task3 = create_task(user=self.user, project_id=self.project.id, status="done")

        res = self.client.get(f"{TASK_URL}?status=todo&page_size=10")
        self.assertEqual(200, res.status_code)
        results = res.data.get("results", res.data.get("data", res.data))
        self.assertEqual(1, len(results))
        result_content = results[0]
        self.assertEqual(task1.project.id, result_content["project_id"])
        self.assertEqual(task1.status, result_content["status"])

    def test_search_by_title_description(self):
        task1 = create_task(
            user=self.user,
            project_id=self.project.id,
            title="Check signal test",
            description="temp description",
        )
        task2 = create_task(
            user=self.user,
            project_id=self.project.id,
            title="Testing",
            description="testing signal test",
        )
        task3 = create_task(
            user=self.user,
            project_id=self.project.id,
            title="simple title",
            description="simple descriptiom",
        )

        res = self.client.get(
            f"{TASK_URL}?search=signal&sort=created_at&dir=asc&page_size=10"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data.get("data", res.data))
        self.assertEqual(2, len(results))
        self.assertEqual(task1.title, results[0]["title"])
        self.assertEqual(task1.description, results[0]["description"])
        self.assertEqual(task2.title, results[1]["title"])
        self.assertEqual(task2.description, results[1]["description"])

    def test_sort_desc_due_date(self):
        task1 = create_task(
            user=self.user, project_id=self.project.id, due_date=date(2025, 1, 5)
        )
        task2 = create_task(
            user=self.user, project_id=self.project.id, due_date=date(2025, 1, 3)
        )
        task3 = create_task(
            user=self.user, project_id=self.project.id, due_date=date(2025, 1, 6)
        )
        res = self.client.get(f"{TASK_URL}?sort=due_date&dir=desc&page_size=10")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data.get("data", res.data))

        ids_returned_in_order = [item["id"] for item in results]
        self.assertEqual(ids_returned_in_order, [task3.id, task1.id, task2.id])

    def test_sort_desc_created_at_date(self):
        task1 = create_task(user=self.user, project_id=self.project.id)
        task2 = create_task(user=self.user, project_id=self.project.id)
        task3 = create_task(user=self.user, project_id=self.project.id)
        res = self.client.get(f"{TASK_URL}?sort=created_at&dir=desc&page_size=10")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data.get("data", res.data))
        self.assertEqual(3, len(results))
        ids_returned_in_order = [item["id"] for item in results]
        self.assertEqual(ids_returned_in_order, [task3.id, task2.id, task1.id])

    def test_try_get_nonexistent_task(self):
        url = default_url(999999)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task_partial(self):
        task = create_task(user=self.user, project_id=self.project.id)

        updatePayload = {
            "title": "update task unit test",
            "description": "testing basic crud - update",
            "status": "todo",
            "priority": "low",
        }

        update_url = default_url(task.id)
        res = self.client.patch(update_url, updatePayload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "update task unit test")
        self.assertEqual(task.description, "testing basic crud - update")
        self.assertEqual(task.status, "todo")
        self.assertEqual(task.priority, "low")

    def test_update_task_invalid_priority(self):
        task = create_task(user=self.user, project_id=self.project.id)

        updatePayload = {
            "priority": "danger",
        }

        update_url = default_url(task.id)
        res = self.client.patch(update_url, updatePayload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        task.refresh_from_db()

    def test_update_task_invalid_status(self):
        task = create_task(user=self.user, project_id=self.project.id)

        updatePayload = {
            "status": "down",
        }

        update_url = default_url(task.id)
        res = self.client.patch(update_url, updatePayload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        task.refresh_from_db()

    def test_update_task_full(self):
        task = create_task(user=self.user, project_id=self.project.id)

        updatePayload = {
            "project_id": self.project.id,
            "title": "update task unit test",
            "description": "testing basic crud - update",
            "status": "todo",
            "priority": "low",
            "due_date": "2030-01-15",
            "estimate_minutes": 10,
        }

        update_url = default_url(task.id)
        res = self.client.put(update_url, updatePayload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()

        self.assertEqual(task.project_id, self.project.id)
        self.assertEqual(task.title, updatePayload["title"])
        self.assertEqual(task.description, updatePayload["description"])
        self.assertEqual(task.status, updatePayload["status"])
        self.assertEqual(task.priority, updatePayload["priority"])
        self.assertEqual(task.due_date, date(2030, 1, 15))
        self.assertEqual(task.estimate_minutes, updatePayload["estimate_minutes"])

    def test_delete_task(self):
        task = create_task(user=self.user, project_id=self.project.id)
        url = default_url(task.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
