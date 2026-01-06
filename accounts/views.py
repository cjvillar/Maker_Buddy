from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from awards.models import UserAward


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_awards = (
        profile_user.awards.select_related("award").all().order_by("-awarded_at")
    )

    projects = profile_user.maker_projects.select_related("owner").order_by(
        "-created_at"
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "projects": projects,
            "user_awards": user_awards,
        },
    )


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"form": form})
