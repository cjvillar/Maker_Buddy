from decimal import Decimal
from django.test import TestCase
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from maker_parts.models import ComponentPrice, ProjectPart
from maker_parts.tests.factories import make_component, make_price


class ComponentModelTests(TestCase):

    def test_latest_price_returns_most_recent(self):
        c = make_component()
        old = make_price(c, unit_price="1.00")
        # Manually backdate the first price
        ComponentPrice.objects.filter(pk=old.pk).update(
            fetched_at=timezone.now() - timedelta(days=2)
        )
        new = make_price(c, unit_price="2.00")
        self.assertEqual(c.latest_price.pk, new.pk)

    def test_is_stale_true_when_over_7_days(self):
        c = make_component(last_synced=timezone.now() - timedelta(days=8))
        self.assertTrue(c.is_stale)

    def test_is_stale_false_when_recently_synced(self):
        c = make_component(last_synced=timezone.now() - timedelta(days=3))
        self.assertFalse(c.is_stale)


class ProjectPartModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testmaker", password="pass")
        # Import here to avoid circular imports at module level
        from maker_projects.models import MakerProject

        self.project = MakerProject.objects.create(
            owner=self.user,
            title="Test Project",
            status="active",
        )
        self.component = make_component()

    def _make_project_part(self, quantity=1):
        return ProjectPart.objects.create(
            project=self.project,
            component=self.component,
            quantity=quantity,
        )

    def test_line_total_with_price(self):
        make_price(self.component, unit_price="4.99")
        pp = self._make_project_part(quantity=3)
        self.assertEqual(pp.line_total, Decimal("14.97"))

    def test_line_total_none_without_price(self):
        pp = self._make_project_part()
        self.assertIsNone(pp.line_total)

    def test_bom_total_sums_all_parts(self):
        c2 = make_component(
            digikey_part_number="TEST-002-ND", manufacturer_pn="TEST002"
        )
        make_price(self.component, unit_price="4.99")
        make_price(c2, unit_price="1.00")
        ProjectPart.objects.create(
            project=self.project, component=self.component, quantity=2
        )
        ProjectPart.objects.create(project=self.project, component=c2, quantity=5)
        # 4.99 * 2 + 1.00 * 5 = 9.98 + 5.00 = 14.98
        self.assertEqual(ProjectPart.bom_total(self.project), Decimal("14.98"))

    def test_duplicate_part_raises_integrity_error(self):
        from django.db import IntegrityError

        self._make_project_part()
        with self.assertRaises(IntegrityError):
            self._make_project_part()
