from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserProfSignalTests(TestCase):
    def test_profile_created_when_user_created(self):
        user = User.objects.create_user(
            username="test_user",
            password="password123"
        )

        self.assertTrue(
            UserProfile.objects.filter(user=user).exists()
        )
        
        self.assertEqual(user.profile.user, user)
