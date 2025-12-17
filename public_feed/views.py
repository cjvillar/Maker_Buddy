from django.shortcuts import render
from maker_projects.models import MakerProject


# Create your views here.
def public_feed(request):
    projects = MakerProject.objects.all()
    return render(
        request,
        "public_feed/feed.html",
        {"projects": projects},
    )
