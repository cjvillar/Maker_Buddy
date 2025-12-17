from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
from maker_projects.models import Project
from django.urls import reverse


class SignupTests(TestCase):
    def test_user_sign_up(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "test_user",
                "password1": "STRONGPass123!",
                "password2": "STRONGPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="test_user").exists())


class ProfileEditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="PASSword")
        self.client.login(username="test_user", password="PASSword")

    def test_edit_profile_page_loads(self):
        response = self.client.get(reverse("accounts:edit_profile"))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_success(self):
        response = self.client.post(
            reverse("accounts:edit_profile"),
            {"display_name": "New Name", "bio": "Updated bio"},
        )
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "New Name")
        self.assertEqual(self.user.profile.bio, "Updated bio")
        self.assertRedirects(response, reverse("accounts:profile", args=["test_user"]))


# TODO move integration test
class ProfileTests(TestCase):
    def test_profile_projects(self):
        user = User.objects.create_user(username="test_user", password="password123")

        Project.objects.create(owner=user, title="Test Project", description="Desc")

        response = self.client.get(reverse("accounts:profile", args=["test_user"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
