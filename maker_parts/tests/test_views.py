from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from maker_parts.tests.factories import make_component
from maker_parts.models import ProjectPart


class ComponentListViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="maker", password="pass")
        self.client.login(username="maker", password="pass")
        self.url = reverse("maker_parts:component_list")

        self.c1 = make_component(
            digikey_part_number="TEST-001-ND",
            manufacturer_pn="ATMEGA328",
            description="8-bit AVR microcontroller",
            category="Microcontrollers",
        )
        self.c2 = make_component(
            digikey_part_number="TEST-002-ND",
            manufacturer_pn="NE555",
            description="Timer IC",
            category="Integrated Circuits",
        )

    def test_search_by_manufacturer_pn(self):
        resp = self.client.get(self.url, {"q": "ATMEGA"})
        self.assertContains(resp, "ATMEGA")
        self.assertNotContains(resp, "NE555")

    def test_filter_by_category(self):
        resp = self.client.get(self.url, {"category": "Microcontrollers"})
        self.assertContains(resp, "8-bit AVR microcontroller")
        self.assertNotContains(resp, "Timer IC")

    def test_inactive_components_not_shown(self):
        self.c1.is_active = False
        self.c1.save()
        resp = self.client.get(self.url)
        self.assertNotContains(resp, "ATMEGA328")

    def test_redirects_anonymous_user(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class AddToProjectViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="maker", password="pass")
        self.client.login(username="maker", password="pass")
        self.component = make_component()

        from maker_projects.models import MakerProject

        self.project = MakerProject.objects.create(
            owner=self.user,
            title="My Project",
            status="active",
        )

    def _post(self, quantity=1, notes="", project_id=None):
        data = {
            "quantity": quantity,
            "notes": notes,
            "next": "/parts/",
            "project_id": project_id or self.project.pk,
        }
        return self.client.post(
            reverse("maker_parts:add_to_project", args=[self.component.pk]),
            data,
        )

    def test_no_active_project_redirects_with_warning(self):
        self.project.status = "completed"
        self.project.save()
        # posting without a valid project_id now returns 404
        resp = self.client.post(
            reverse("maker_parts:add_to_project", args=[self.component.pk]),
            {"quantity": 1, "notes": "", "next": "/parts/"},
        )
        self.assertEqual(resp.status_code, 404)


class RemoveFromProjectViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")

        from maker_projects.models import MakerProject

        self.project = MakerProject.objects.create(
            owner=self.owner,
            title="My Project",
            status="active",
        )
        self.component = make_component()
        self.pp = ProjectPart.objects.create(
            project=self.project,
            component=self.component,
            quantity=1,
        )

    def test_owner_can_remove_part(self):
        self.client.login(username="owner", password="pass")
        self.client.post(reverse("maker_parts:remove_from_project", args=[self.pp.pk]))
        self.assertFalse(ProjectPart.objects.filter(pk=self.pp.pk).exists())

    def test_non_owner_gets_404(self):
        self.client.login(username="other", password="pass")
        resp = self.client.post(
            reverse("maker_parts:remove_from_project", args=[self.pp.pk])
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(ProjectPart.objects.filter(pk=self.pp.pk).exists())
