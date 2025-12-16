from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="maker_projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
