from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User
from maker_projects.models import MakerProject
from public_feed.views import PublicFeedView


class PublicFeedViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        # Create 6 projects so we can test pagination (paginate_by = PublicFeedView.paginate_by)
        for i in range(6):
            MakerProject.objects.create(
                title=f"Project {i}",
                owner=cls.user,
                status="completed",
                created_at=timezone.now() - timezone.timedelta(days=i),
            )

    def test_view_status_code(self):
        response = self.client.get(reverse("public_feed:home"))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse("public_feed:home"))
        self.assertTemplateUsed(response, "public_feed/feed.html")

    def test_context_object_name(self):
        response = self.client.get(reverse("public_feed:home"))
        self.assertIn("projects", response.context)

    def test_ordering_is_newest_first(self):
        response = self.client.get(reverse("public_feed:home"))
        projects = response.context["projects"]

        dates = [project.created_at for project in projects]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_pagination_first_page(self):
        response = self.client.get(reverse("public_feed:home"))
        self.assertEqual(len(response.context["projects"]), PublicFeedView.paginate_by)
        self.assertTrue(response.context["is_paginated"])

    def test_pagination_second_page(self):
        response = self.client.get(reverse("public_feed:home") + "?page=2")
        paginator = response.context["paginator"]
        remaining = paginator.count - paginator.per_page
        self.assertEqual(len(response.context["projects"]), remaining)
