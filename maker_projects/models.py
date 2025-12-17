from django.db import models
from django.contrib.auth.models import User


class MakerProject(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="maker_projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    code_snippet = models.TextField(blank=True)
    image = models.ImageField(upload_to="project_images/", blank=True)

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
