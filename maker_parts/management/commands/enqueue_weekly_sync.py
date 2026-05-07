"""
maker_parts/management/commands/enqueue_weekly_sync.py

Enqueues the weekly DigiKey sync task into the django-tasks-db queue.
Run this from a cron job once a week.

Usage:
    python manage.py enqueue_weekly_sync

"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Enqueue the weekly DigiKey parts sync task."

    def handle(self, *args, **options):
        from maker_parts.tasks import weekly_sync_all_parts

        result = weekly_sync_all_parts.enqueue()
        self.stdout.write(
            self.style.SUCCESS(f"Enqueued weekly sync. Task id: {result.id}")
    )
