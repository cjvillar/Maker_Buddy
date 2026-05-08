from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse


class GitHubWhitelistAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        if sociallogin.account.provider != "github":
            return

        username = sociallogin.account.extra_data.get("login")
        allowed = getattr(settings, "ALLOWED_GITHUB_USERNAMES", set())

        if not username or username not in allowed:
            raise ImmediateHttpResponse(redirect("/account/unauthorized/"))

    def is_auto_signup_allowed(self, request, sociallogin):
        username = sociallogin.account.extra_data.get("login")
        allowed = getattr(settings, "ALLOWED_GITHUB_USERNAMES", set())

        if not username or username not in allowed:
            return False

        return super().is_auto_signup_allowed(request, sociallogin)
