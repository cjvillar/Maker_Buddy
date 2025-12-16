from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "bio", "profile_pic"]  # editable fields
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
