from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile

class UserProfileSignalTest(TestCase):
    def test_profile_created_on_user_save(self):
        # trigger post_save signal
        user = User.objects.create_user(username='testuser', password='password123')
        
        # Check if profile exists and is linked correctly
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.user.username, 'testuser')
