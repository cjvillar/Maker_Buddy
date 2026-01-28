from django import forms

from .models import MakerProject, CheckPoint,ProjectLink


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "due_date", "image"]
        widgets = {"due_date": forms.SelectDateWidget(attrs={"type": "date"})}


class CheckPointForm(forms.ModelForm):
    class Meta:
        model = CheckPoint
        fields = ["title", "description"]


class ProjectLinkForm(forms.ModelForm):
    class Meta:
        model = ProjectLink
        fields = ["url"]

    def clean_url(self):
        url = self.cleaned_data["url"]
        if not url.startswith("https://"):
            raise forms.ValidationError("Links must use HTTPS")
        return url
    
