from django import forms
from .models import MakerProject, CheckPoint


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "due_date", "image", "code_snippet"]
        widgets = {"due_date": forms.SelectDateWidget(attrs={"type": "date"})}


class CheckPointForm(forms.ModelForm):
    class Meta:
        model = CheckPoint
        fields = ["title", "description"]
