from django import forms
from .models import MakerProject


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "image", "code_snippet"]
