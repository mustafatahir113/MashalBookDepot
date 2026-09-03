from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = CustomUser

        fields = [
            'username',
            'email',
            'phone',
            'gender',
            'password1',
            'password2'
        ]

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if CustomUser.objects.filter(email__iexact=email).exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = CustomUser

        fields = [
            'email',
            'phone'
        ]

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if CustomUser.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        ).exists():

            raise forms.ValidationError(
                "This email is already being used by another account."
            )

        return email