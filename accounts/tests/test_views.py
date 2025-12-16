from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class SignupTests(TestCase):
    def test_user_can_sign_up(self):
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
