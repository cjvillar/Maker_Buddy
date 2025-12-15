from django.shortcuts import render

# Create your views here.
def public_feed(request):
    return render(request, "test.html", {
        "title": "Accounts App"
    })