from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Award(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="awards/", blank=True)

    def __str__(self):
        return self.name


class UserAward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="awards")
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "award")
