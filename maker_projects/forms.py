from django import forms

from .models import MakerProject, ProjectFeature, ProjectLink


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "due_date", "image", "goal"]
        widgets = {
             "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control custom-file-input", "accept": "image/*"}
            ),
        }


class ProjectFeatureForm(forms.ModelForm):
    class Meta:
        model = ProjectFeature
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
