from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User


class MakerProject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="maker_projects"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    code_snippet = models.TextField(blank=True)
    image = models.ImageField(upload_to="project_images/", blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner"],
                condition=Q(status="active"),
                name="one_active_project_per_user",
            ),
        ]

    def is_overdue(self):
        return (
            self.due_date
            and self.status != self.Status.COMPLETED
            and self.due_date < timezone.now().date()
        )

    def days_remaining(self):
        if not self.due_date:
            return None
        return (self.due_date - timezone.now().date()).days

    def __str__(self):
        return self.title


class CheckPoint(models.Model):
    project = models.ForeignKey(
        MakerProject, on_delete=models.CASCADE, related_name="checkpoints"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_complete = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} – {self.title}"


# NOTE: might not keep, just test for now
class ProjectLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_likes"
    )
    project = models.ForeignKey(
        MakerProject, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_user_project_like",
            )
        ]
