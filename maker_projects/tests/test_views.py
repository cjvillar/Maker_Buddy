from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from maker_projects.models import MakerProject, ProjectLike, BuildStep
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


class BuildStepTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_user", password="pass")
        self.client.login(username="test_user", password="pass")
        self.project = MakerProject.objects.create(
            owner=self.user,
            title="Test Project",
            description="Test description",
            status=MakerProject.Status.ACTIVE,
        )

    def test_build_step_created(self):
        step = BuildStep.objects.create(
            project=self.project,
            title="Connect wires",
            description="l1 -> l3",
            order=0,
        )
        self.assertEqual(self.project.build_steps.count(), 1)
        self.assertEqual(step.title, "Connect wires")
        self.assertEqual(step.order, 0)
        self.assertFalse(step.is_complete)

    def test_add_step_view(self):
        url = reverse("maker_projects:build_step_add", args=[self.project.pk])
        response = self.client.post(
            url, {"title": "First step", "description": "Do this"}
        )
        self.assertEqual(self.project.build_steps.count(), 1)
        self.assertRedirects(
            response, reverse("maker_projects:edit", args=[self.project.pk])
        )

    def test_add_step_requires_title(self):
        url = reverse("maker_projects:build_step_add", args=[self.project.pk])
        self.client.post(url, {"title": "", "description": "No title"})
        self.assertEqual(self.project.build_steps.count(), 0)

    def test_add_step_order_auto_assigned(self):
        url = reverse("maker_projects:build_step_add", args=[self.project.pk])
        self.client.post(url, {"title": "Step one", "description": ""})
        self.client.post(url, {"title": "Step two", "description": ""})
        steps = list(self.project.build_steps.order_by("order"))
        self.assertEqual(steps[0].order, 0)
        self.assertEqual(steps[1].order, 1)

    def test_edit_step(self):
        step = BuildStep.objects.create(
            project=self.project, title="Old title", order=0
        )
        url = reverse("maker_projects:build_step_edit", args=[step.pk])
        self.client.post(
            url,
            {
                "action": "save",
                "title": "New title",
                "description": "",
                "order": 0,
                "is_complete": False,
            },
        )
        step.refresh_from_db()
        self.assertEqual(step.title, "New title")

    def test_delete_step_via_edit_view(self):
        step = BuildStep.objects.create(
            project=self.project, title="To delete", order=0
        )
        url = reverse("maker_projects:build_step_edit", args=[step.pk])
        self.client.post(url, {"action": "delete"})
        self.assertFalse(BuildStep.objects.filter(pk=step.pk).exists())
