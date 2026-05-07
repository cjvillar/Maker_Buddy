from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from maker_projects.models import MakerProject, ProjectLike
from django.db import IntegrityError


class CreateProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.client.login(username="test_user", password="pass")

    def test_create_project(self):
        project = MakerProject.objects.create(
            owner=self.user,
            title="My First Project",
            description="Hello world",
            status=MakerProject.Status.ACTIVE,
        )
        self.assertTrue(MakerProject.objects.filter(title="My First Project").exists())

    def test_one_active_project(self):

        MakerProject.objects.create(
            owner=self.user,
            title="First",
            description="Desc",
            status=MakerProject.Status.ACTIVE,
        )

        with self.assertRaises(IntegrityError):
            MakerProject.objects.create(
                owner=self.user,
                title="Second",
                description="Desc",
                status=MakerProject.Status.ACTIVE,
            )


class DeleteProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.client.login(username="test_user", password="pass")
        self.project = MakerProject.objects.create(
            owner=self.user,
            title="My NEW Project",
            description="Some mistake to edit",
        )

    def test_owner_edit_project(self):
        response = self.client.get(
            reverse("maker_projects:edit", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)


class ProjectDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.project = MakerProject.objects.create(
            owner=self.user,
            title="Test Project",
            description="Test description",
            status=MakerProject.Status.ACTIVE,
        )
        ProjectLike.objects.create(user=self.user, project=self.project)
        self.client.login(username="test_user", password="pass")

    def test_project_detail_page(self):
        url = reverse("maker_projects:detail", args=[self.project.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST PROJECT")  # template forces uppercase
        self.assertRegex(
            response.content.decode(), r"LIKES\s*<span.*>.*1.*</span>"
        )  # gets likes count from the bootstrap baadge
