from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user1", password="PASSword123"
        )

    def test_user_can_log_in(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_user1",
                "password": "PASSword123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
