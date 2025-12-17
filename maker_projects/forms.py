from django import forms
from .models import MakerProject, CheckPoint


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "image", "code_snippet"]


class CheckPointForm(forms.ModelForm):
    class Meta:
        model = CheckPoint
        fields = ["title", "description"]
