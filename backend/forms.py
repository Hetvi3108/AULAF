from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Item, Claim


class AURegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@ahduni.edu.in"):
            raise forms.ValidationError("Only Ahmedabad University email is allowed!")
        return email


class ItemForm(forms.ModelForm):
    class Meta:
        model   = Item
        exclude = ["reported_by", "status",]

    def clean(self):
        cleaned_data    = super().clean()
        submission_type = cleaned_data.get("submission_type")
        location        = cleaned_data.get("submitted_at")
        if submission_type == "desk" and not location:
            self.add_error("submitted_at", "Location is required for desk submission")
        return cleaned_data


class ClaimForm(forms.ModelForm):
    class Meta:
        model   = Claim
        fields  = ["claimer_name", "enrollment_no", "au_email", "id_card_photo"]
        widgets = {
            "claimer_name":  forms.TextInput(attrs={"placeholder": "Full Name"}),
            "enrollment_no": forms.TextInput(attrs={"placeholder": "Enrollment Number"}),
            "au_email":      forms.EmailInput(attrs={"placeholder": "AU Email (@ahduni.edu.in)"}),
        }

    # ✅ Validate AU email domain
    def clean_au_email(self):
        email = self.cleaned_data.get("au_email")
        if not email.endswith("@ahduni.edu.in"):
            raise forms.ValidationError("Only @ahduni.edu.in email is accepted!")
        return email