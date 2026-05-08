from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


# Using allAuth 9github social log in) need to come up with a test
class AuthTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = User.objects.create_user(
            username="test_user1", password="PASSword123"
        )

    def test_user_can_log_in(self):
        self.client.force_login(self.user)
        self.assertTrue(self.client.session["_auth_user_id"])
