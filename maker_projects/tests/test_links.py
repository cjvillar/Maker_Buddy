from django.test import TestCase
from django.contrib.auth.models import User
from maker_projects.models import MakerProject, ProjectLink
from maker_projects.forms import ProjectLinkForm

class ProjectLinksTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("test_user", password="pass")
        self.project = MakerProject.objects.create(
            owner=user,
            title="Test Project",
            description="Test description",
        )
        
    def test_create_github_link(self):
        link = ProjectLink.objects.create(
            project=self.project,
            link_type=ProjectLink.LinkType.GITHUB,
            url="https://github.com/testuser/testrepo"
        )

        self.assertEqual(link.project, self.project)
        self.assertEqual(link.link_type, ProjectLink.LinkType.GITHUB)
        self.assertEqual(str(link), "GitHub: https://github.com/testuser/testrepo")

    def test_raises_validation_error(self):
        # attempting to create a HTTP GitHub link should fail
        form = ProjectLinkForm(data={
            "project": self.project.id,
            "link_type": ProjectLink.LinkType.GITHUB,
            "url": "http://github.com/testuser/testrepo"
        })

        self.assertFalse(form.is_valid())
        self.assertIn("HTTPS", form.errors["url"][0])

