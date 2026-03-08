from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from awards.models import UserAward

from django.contrib import messages
from allauth.account.views import SignupView
from allauth.account import app_settings


# class CustomSignupView(SignupView):
#     def form_valid(self, form):

#         response = super().form_valid(form)

#         if app_settings.EMAIL_VERIFICATION_SETTING == app_settings.EmailVerificationMethod.MANDITORY:
#             messages.info(self.request, "WE SENT AN EMAIL ...")
#         else:
#             messages.success(self.request, "YOU GOOD BRAH")
#         return response

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "account/signup.html", {"form": form})


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
        "account/profile.html",
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

    return render(request, "account/edit_profile.html", {"form": form})
