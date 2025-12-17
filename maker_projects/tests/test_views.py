
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from maker_projects.models import MakerProject

class CreateProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.client.login(username="test_user", password="pass")

    def test_create_project(self):
        response = self.client.post(
            reverse("maker_projects:create"),
            {
                "title": "My First Project",
                "description": "Hello world",
                "code_snippet": "print('hi')",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            MakerProject.objects.filter(title="My First Project").exists()
        )
