"""
parts/management/commands/seed_parts.py

Fetch a list of DigiKey part numbers from a JSON or CSV file and
upsert them into the local database.

Usage:
    python manage.py seed_parts --file parts/data/seed_parts.json
    python manage.py seed_parts --file parts/data/seed_parts.csv
    python manage.py seed_parts --file parts/data/seed_parts.json --dry-run

File formats accepted
─────────────────────
JSON  →  a flat list of DigiKey part numbers:
    ["2648-SC0915TR-ND", "1276-1069-1-ND", "296-1381-1-ND"]

CSV   →  one part number per line (header row optional, it is auto-detected):
    digikey_part_number
    2648-SC0915TR-ND
    1276-1069-1-ND
"""

from __future__ import annotations

import csv
import json
import logging
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from maker_parts.services.digikey import DigiKeyClient, DigiKeyRateLimitError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed the parts catalog from a JSON or CSV file of DigiKey part numbers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            type=Path,
            help="Path to JSON or CSV file containing DigiKey part numbers.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would be fetched without writing to the database.",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.3,
            help="Seconds to wait between API calls (default: 0.3).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Stop after fetching this many parts (useful for testing).",
        )

    def handle(self, *args, **options):
        file_path: Path = options["file"]
        dry_run: bool = options["dry_run"]
        delay: float = options["delay"]
        limit = options["limit"]

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        part_numbers = self._load_part_numbers(file_path)

        if not part_numbers:
            raise CommandError("No part numbers found in file.")

        if limit:
            part_numbers = part_numbers[:limit]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"{'[DRY RUN] ' if dry_run else ''}"
                f"Seeding {len(part_numbers)} parts from {file_path.name} …"
            )
        )

        client = DigiKeyClient()
        ok = skipped = errors = 0

        for i, pn in enumerate(part_numbers, start=1):
            self.stdout.write(f"  [{i}/{len(part_numbers)}] {pn} … ", ending="")

            if dry_run:
                self.stdout.write(self.style.WARNING("skipped (dry run)"))
                continue

            try:
                part_data = client.get_part(pn)
                self._upsert_part(part_data)
                self.stdout.write(self.style.SUCCESS("OK"))
                ok += 1
            except DigiKeyRateLimitError:
                wait = 60
                self.stdout.write(self.style.ERROR(f"RATE LIMITED — waiting {wait}s …"))
                time.sleep(wait)
                # retry once after back-off
                try:
                    part_data = client.get_part(pn)
                    self._upsert_part(part_data)
                    self.stdout.write(self.style.SUCCESS("OK (after retry)"))
                    ok += 1
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"FAILED: {exc}"))
                    errors += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"ERROR: {exc}"))
                logger.exception("Failed to fetch part %s", pn)
                errors += 1

            time.sleep(delay)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\nDone. OK={ok}  skipped={skipped}  errors={errors}"
            )
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_part_numbers(self, path: Path) -> list[str]:
        suffix = path.suffix.lower()

        if suffix == ".json":
            data = json.loads(path.read_text())
            if not isinstance(data, list):
                raise CommandError(
                    "JSON file must be a flat list of part number strings."
                )
            return [str(p).strip() for p in data if str(p).strip()]

        if suffix == ".csv":
            numbers = []
            with path.open(newline="") as fh:
                reader = csv.reader(fh)
                for row in reader:
                    if not row:
                        continue
                    value = row[0].strip()
                    # Skip header rows (non-numeric first character is a hint,
                    # but the most reliable check is whether it looks like a
                    # real part number — skip obviously header-ish values).
                    if value.lower() in ("digikey_part_number", "part_number", "part"):
                        continue
                    if value:
                        numbers.append(value)
            return numbers

        raise CommandError(f"Unsupported file type: {suffix!r}. Use .json or .csv.")

    def _upsert_part(self, part_data: dict) -> None:
        """Write the normalised part dict to the database."""
        from maker_parts.models import Component, ComponentPrice
        from django.utils import timezone

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
            "UPSERT %s %s — %s @ $%s (%s in stock)",
            action,
            part_data["digikey_part_number"],
            part_data["description"][:60],
            part_data["unit_price"],
            part_data.get("quantity_available"),
        )
