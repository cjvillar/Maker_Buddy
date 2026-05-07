from decimal import Decimal
from maker_parts.models import Component, ComponentPrice, SyncSource


# Fixtures
def make_component(**kwargs) -> Component:
    defaults = {
        "digikey_part_number": "TEST-001-ND",
        "manufacturer_pn": "TEST001",
        "manufacturer": "Test Corp",
        "description": "A test component",
        "category": "Test Category",
        "is_active": True,
        "sync_source": SyncSource.DIGIKEY,
    }
    defaults.update(kwargs)
    return Component.objects.create(**defaults)


def make_price(component, unit_price="4.99", stock_qty=100, **kwargs) -> ComponentPrice:
    return ComponentPrice.objects.create(
        component=component,
        unit_price=Decimal(unit_price),
        stock_qty=stock_qty,
        **kwargs,
    )
