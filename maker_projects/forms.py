from .models import MakerProject, ProjectFeature, ProjectLink
from django import forms


class ProjectBasicForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description"]


class ProjectTimelineForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"})
        }


# TODO: https://forum.djangoproject.com/t/styling-clearablefileinput/31501
# custom format ClearableFileInput, seems like pain
class ProjectMediaGoalForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["image", "goal"]
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "form-control custom-file-input",
                    "accept": "image/*",
                }
            )
        }


class MakerProjectForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["title", "description", "due_date", "image", "goal"]
        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "image": forms.FileInput(  # was ClearableFileInput but this has default clear widget I dont want
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

    url = forms.URLField(required=False)

    def clean_url(self):
        url = self.cleaned_data.get("url", "")
        if url and not url.startswith("https://"):
            raise forms.ValidationError("Links must use HTTPS")
        return url
