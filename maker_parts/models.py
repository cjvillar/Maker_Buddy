"""
maker_parts/models.py

Component: metadata about a part (manufacturer, description, etc.)
ComponentPrice: time-stamped price + stock snapshot from a distributor

Design notes:
Component and ComponentPrice are intentionally separate as Component rows change rarely.
ComponentPrice rows are written on every sync and keep a history.
pricing_tiers is a JSONField
sync_source tracks which API provided the data so Mouser can coexist later.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SyncSource(models.TextChoices):
    DIGIKEY = "digikey", "DigiKey"
    MOUSER = "mouser", "Mouser"  # TODO: Get Mouser API cred


class Component(models.Model):
    """
    A single electronic component in the catalog.
    One row per unique DigiKey (or Mouser) part number.
    """

    digikey_part_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="DigiKey's own part number, e.g. '2648-SC0915TR-ND'",
    )
    manufacturer_pn = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Manufacturer's part number, e.g. 'ATmega328P-PU'",
    )
    manufacturer = models.CharField(max_length=150, blank=True)

    description = models.TextField(blank=True)
    category = models.CharField(max_length=150, blank=True, db_index=True)
    product_url = models.URLField(max_length=500, blank=True)
    datasheet_url = models.URLField(max_length=500, blank=True)

    sync_source = models.CharField(
        max_length=20,
        choices=SyncSource.choices,
        default=SyncSource.DIGIKEY,
    )
    last_synced = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Set False when a part goes EOL or is delisted.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["manufacturer", "manufacturer_pn"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer_pn} ({self.digikey_part_number})"

    @property
    def latest_price(self) -> "ComponentPrice | None":
        """Most recent price snapshot for quick access in templates."""
        return self.prices.order_by("-fetched_at").first()

    @property
    def is_stale(self) -> bool:
        """True if the part hasn't been synced in over 7 days."""
        if not self.last_synced:
            return True
        return (timezone.now() - self.last_synced).days > 7


class ComponentPrice(models.Model):
    """
    A price + stock snapshot for a Component at a point in time.

    A new row is created on every sync rather than updating in place,
    so you get a price history for free.  Query with:
        component.prices.order_by("-fetched_at").first()
    """

    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="prices",
    )
    distributor = models.CharField(
        max_length=20,
        choices=SyncSource.choices,
        default=SyncSource.DIGIKEY,
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Single-unit price in USD.",
    )
    stock_qty = models.IntegerField(
        default=0,
        help_text="Units available at time of sync.",
    )

    # Break-quantity pricing tiers stored as JSON, e.g.:
    # [{"break_qty": 1, "unit_price": 2.5}, {"break_qty": 10, "unit_price": 2.1}]
    pricing_tiers = models.JSONField(default=list, blank=True)

    fetched_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-fetched_at"]
        indexes = [
            models.Index(fields=["component", "-fetched_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.component.digikey_part_number} @ "
            f"${self.unit_price} ({self.fetched_at:%Y-%m-%d})"
        )


class ProjectPart(models.Model):
    """
    Join model linking a Component to a MakerProject (the BOM).

    Kept in maker_parts to avoid a circular import with maker_projects.
    Uses a string reference "maker_projects.MakerProject" for the FK.
    """

    project = models.ForeignKey(
        "maker_projects.MakerProject",
        on_delete=models.CASCADE,
        related_name="parts",
    )
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="project_uses",
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. '10k variant' or 'any 5V regulator works'",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "component"],
                name="unique_part_per_project",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.component.manufacturer_pn} x{self.quantity} → {self.project.title}"
        )

    @property
    def line_total(self):
        """Quantity x latest unit price. Returns None if no price exists."""
        price = self.component.latest_price
        if price and price.unit_price:
            return round(self.quantity * price.unit_price, 2)
        return None

    @classmethod
    def bom_total(cls, project):
        """Sum of all line totals for a project. Returns None if no pricing data."""
        total = None
        for pp in (
            cls.objects.filter(project=project)
            .select_related("component")
            .prefetch_related("component__prices")
        ):
            lt = pp.line_total
            if lt is not None:
                total = (total or 0) + lt
        return total
