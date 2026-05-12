from .models import MakerProject, BuildStep, ProjectLink
from django import forms
from django.forms import inlineformset_factory


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


class ProjectMediaGoalForm(forms.ModelForm):
    class Meta:
        model = MakerProject
        fields = ["image", "goal"]
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control custom-file-input", "accept": "image/*"}
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
            "image": forms.FileInput(
                attrs={"class": "form-control custom-file-input", "accept": "image/*"}
            ),
        }


class BuildStepForm(forms.ModelForm):
    """Used in the create wizard — no is_complete, since a new step can't be done yet."""

    class Meta:
        model = BuildStep
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class BuildStepEditForm(forms.ModelForm):
    """Used when editing existing steps — includes is_complete."""

    class Meta:
        model = BuildStep
        fields = ["title", "description", "order", "is_complete"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "order": forms.NumberInput(attrs={"min": 0}),
        }


BuildStepFormSet = inlineformset_factory(
    MakerProject,
    BuildStep,
    form=BuildStepEditForm,
    extra=1,
    can_delete=True,
)


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
