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
