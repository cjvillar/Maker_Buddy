from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from urllib.parse import urlparse


class MakerProject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="maker_projects"
    )

    title = models.CharField(
        max_length=200, help_text="Give your project a descriptive name."
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Set reasonable timeframe to finish your project.",
    )

    image = models.ImageField(
        upload_to="project_images/",
        blank=True,
        help_text="Please add an image of your hardware.",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    goal = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short, single-sentence goal for the project",
    )

    definition_of_done = models.TextField(
        blank=True,
        help_text="Clear description of when this project is considered complete",
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

    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            # unique if two projects share same title
            while MakerProject.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("maker_projects:detail", kwargs={"slug": self.slug})


class ProjectLink(models.Model):
    DOMAIN_MAP = {
        "github.com": "github",
        "gitlab.com": "gitlab",
        "bitbucket.org": "bitbucket",
        "youtube.com": "video",
        "youtu.be": "video",
    }

    class LinkType(models.TextChoices):
        GITHUB = "github", "GitHub"
        GITLAB = "gitlab", "GitLab"
        BITBUCKET = "bitbucket", "Bitbucket"
        VIDEO = "video", "Demo Video"

    project = models.ForeignKey(
        "MakerProject",
        on_delete=models.CASCADE,
        related_name="links",
    )

    link_type = models.CharField(
        max_length=20,
        choices=LinkType.choices,
        editable=False,
    )

    url = models.URLField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if not self.url:
            return

        parsed = urlparse(self.url)
        domain = parsed.netloc.lower().lstrip("www.")

        for allowed_domain, link_type in self.DOMAIN_MAP.items():
            if domain == allowed_domain or domain.endswith("." + allowed_domain):
                self.link_type = link_type
                return

        raise ValidationError({"url": "Unsupported link domain"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_link_type_display()}: {self.url}"


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


class BuildStep(models.Model):
    project = models.ForeignKey(
        MakerProject,
        on_delete=models.CASCADE,
        related_name="build_steps",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Step {self.order}: {self.title}"


class ProjectRequirement(models.Model):
    project = models.ForeignKey(
        MakerProject,
        on_delete=models.CASCADE,
        related_name="requirements",
    )
    description = models.CharField(max_length=255)
    is_met = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
