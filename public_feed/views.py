from django.shortcuts import render
from maker_projects.models import MakerProject
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

PAGE_SIZE = 4

def public_feed(request):
    projects = MakerProject.objects.all().order_by('-created_at')
    paginator = Paginator(projects, PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    
    try:
        projects_page = paginator.page(page_number)
    except PageNotAnInteger:
        projects_page = paginator.page(1)
    except EmptyPage:
        projects_page = paginator.page(paginator.num_pages)

    return render(
        request,
        "public_feed/feed.html",
        {"projects": projects_page},
    )
