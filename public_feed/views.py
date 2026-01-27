from django.shortcuts import render
from maker_projects.models import MakerProject
from django.views.generic import ListView


class PublicFeedView(ListView):
    model = MakerProject
    template_name = "public_feed/feed.html"
    context_object_name = "projects"
    ordering = "-created_at"
    paginate_by = 4 
