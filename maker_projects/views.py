from django.shortcuts import render


# Create your views here.
def maker_projects(request):
    return render(request, "base.html", {"title": " App"})
