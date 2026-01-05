from django.db.models.signals import post_save
from django.dispatch import receiver
from maker_projects.models import MakerProject
from .services import evaluate_awards
from .registry import PROJECT_AWARDS


# auto call services.py 

@receiver(post_save, sender=MakerProject)
def trigger_project_awards(sender, instance, **kwargs):
    if instance.status == MakerProject.Status.COMPLETED:
        evaluate_awards(instance.owner, PROJECT_AWARDS)