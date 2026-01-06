from django.test import TestCase
from django.contrib.auth import get_user_model
from awards.registry import FirstProjectAward
from awards.models import Award, UserAward
from maker_projects.models import MakerProject


User = get_user_model()


class AwardsRuleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test_user", password="TESTuser123"
        )

        self.award = Award.objects.create(
            code="first_project_complete", name="First Project"
        )

    def test_first_project_award_eligibility(self):
        # project not eligible for award
        self.assertFalse(FirstProjectAward.is_eligible(self.user))

        MakerProject.objects.create(
            owner=self.user, title="Test Project", status=MakerProject.Status.ACTIVE
        )
        self.assertFalse(FirstProjectAward.is_eligible(self.user))

        project = MakerProject.objects.first()
        project.status = MakerProject.Status.COMPLETED
        project.save()

        # eligible
        self.assertTrue(FirstProjectAward.is_eligible(self.user))
