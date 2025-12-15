from django.shortcuts import render

# Create your views here.
def maker_projects(request):
    return render(request, "test.html", {
        "title": " App"
    })