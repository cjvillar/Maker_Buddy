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
        self.assertTrue(MakerProject.objects.filter(title="My First Project").exists())


class DeleteProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.client.login(username="test_user", password="pass")
        self.project = MakerProject.objects.create(
            owner=self.user,
            title="My NEW Project",
            description="Some mistake to edit",
            code_snippet="print('BUFFER OVERFLOW')",
        )

    def test_owner_edit_project(self):
        response = self.client.get(
            reverse("maker_projects:edit", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)


class ProjectDetailTests(TestCase):
    def test_project_detail_page(self):
        user = User.objects.create_user("test_user", password="pass")
        project = MakerProject.objects.create(
            owner=user,
            title="Test Project",
            description="Test description",
        )

        response = self.client.get(reverse("maker_projects:detail", args=[project.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
