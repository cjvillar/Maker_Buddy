"""
background tasks for syncing parts from the DigiKey API.

seed_parts.py (management command) calls DigiKeyClient.bulk_get_parts (digikey.py API)
writes to db with _upsert_part

tasks.py (this file, weekly sync) queries db for existing part numbers
calls DigiKeyClient.bulk_get_parts (digikey.py) writes updated prices back to db


The worker  is built in Django 6.0 no Celery needed:
python manage.py db_worker

From shell:
    from parts.tasks import weekly_sync_all_parts
    weekly_sync_all_parts.enqueue()

From Cron in settings.py:
    # settings.py
    from django.tasks import DEFAULT_TASK_BACKEND_ALIAS
    DJANGO_TASKS = {
        DEFAULT_TASK_BACKEND_ALIAS: {
            "BACKEND": "django.tasks.backends.database.DatabaseTaskBackend",
        }
    }

    Then in AppConfig.ready() — see maker_parts/apps.py.
"""

from __future__ import annotations

import logging

from django.tasks import task
from django.utils import timezone

from maker_parts.services.digikey import (
    DigiKeyClient,
    DigiKeyRateLimitError,
    DigiKeyError,
)

logger = logging.getLogger(__name__)


def _upsert_part(part_data: dict) -> None:
    """
    Write a normalised part dict to the database.
    Creates or updates the Component row, then appends a new ComponentPrice snapshot.
    """
    from maker_parts.models import Component, ComponentPrice

    component, created = Component.objects.update_or_create(
        digikey_part_number=part_data["digikey_part_number"],
        defaults={
            "manufacturer_pn": part_data["manufacturer_pn"],
            "manufacturer": part_data["manufacturer"],
            "description": part_data["description"],
            "product_url": part_data["product_url"],
            "datasheet_url": part_data["datasheet_url"],
            "category": part_data["category"],
            "last_synced": timezone.now(),
            "sync_source": "digikey",
        },
    )

    if part_data.get("unit_price") is not None:
        ComponentPrice.objects.create(
            component=component,
            distributor="digikey",
            unit_price=part_data["unit_price"],
            stock_qty=part_data.get("quantity_available") or 0,
            pricing_tiers=part_data.get("pricing_tiers", []),
        )

    action = "created" if created else "updated"
    logger.info(
        "UPSERT %s %s — %s @ $%s",
        action,
        part_data["digikey_part_number"],
        part_data["description"][:60],
        part_data["unit_price"],
    )


def _get_all_part_numbers() -> list[str]:
    """Return all DigiKey part numbers currently in the database."""
    from maker_parts.models import Component

    return list(
        Component.objects.filter(is_active=True, sync_source="digikey").values_list(
            "digikey_part_number", flat=True
        )
    )


# Tasks


@task()
def sync_single_part(digikey_part_number: str) -> None:
    """
    Refresh one part.  Useful for on-demand updates — e.g. when a user
    views a part that hasn't been synced in over 24 hours.

    Usage:
        from parts.tasks import sync_single_part
        sync_single_part.enqueue("2648-SC0915TR-ND")
    """
    logger.info("sync_single_part: starting for %s", digikey_part_number)
    client = DigiKeyClient()
    try:
        part_data = client.get_part(digikey_part_number)
        _upsert_part(part_data)
        logger.info("sync_single_part: done for %s", digikey_part_number)
    except DigiKeyRateLimitError:
        # Django 6.0 tasks don't auto-retry yet — log clearly so you know
        # to re-enqueue after the rate limit window passes.
        logger.error(
            "sync_single_part: rate limited fetching %s — re-enqueue manually.",
            digikey_part_number,
        )
        raise
    except DigiKeyError as exc:
        logger.error("sync_single_part: failed for %s: %s", digikey_part_number, exc)
        raise


@task()
def weekly_sync_all_parts() -> None:
    """
    Full catalog refresh — intended to run once a week.

    This is the task to enqueue from your cron job or AppConfig.ready() schedule.
    It pulls every known part number from the DB and refreshes prices/stock.

    Flow:
        weekly_sync_all_parts.enqueue()
            → _get_all_part_numbers()          reads DB
            → DigiKeyClient.bulk_get_parts()   hits DigiKey API (with polite delay)
            → _upsert_part() for each result   writes DB

    If DigiKey rate-limits us mid-batch, the task raises immediately.
    Parts processed before the rate limit are already saved — the next
    run (or a manual re-enqueue) will pick up where it left off because
    bulk_get_parts() is stateless.
    """
    started_at = timezone.now()
    logger.info("weekly_sync_all_parts: started at %s", started_at)

    part_numbers = _get_all_part_numbers()

    if not part_numbers:
        logger.warning("weekly_sync_all_parts: no parts in DB to sync — nothing to do.")
        return

    logger.info("weekly_sync_all_parts: syncing %d parts.", len(part_numbers))

    client = DigiKeyClient()
    results = client.bulk_get_parts(part_numbers)  # handles per-part errors internally

    ok = errors = skipped = 0
    for pn, part_data in results.items():
        if part_data is None:
            skipped += 1
            continue
        try:
            _upsert_part(part_data)
            ok += 1
        except Exception as exc:
            logger.error("weekly_sync_all_parts: upsert failed for %s: %s", pn, exc)
            errors += 1

    logger.info(
        "weekly_sync_all_parts: finished. ok=%d  skipped=%d  errors=%d  duration=%s",
        ok,
        skipped,
        errors,
        timezone.now() - started_at,
    )
