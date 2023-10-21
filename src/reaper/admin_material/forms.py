from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
    UsernameField,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Name"}),
    )
    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    allergies_type = forms.CharField(
        label=_("Allergies Type"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Allergies Type"}
        ),
    )
    fav_adresse = forms.CharField(
        label=_("Favorite Address"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Favorite Address"}
        ),
    )
    fav_adresse_country = forms.CharField(
        label=_("Favorite Address Country"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Favorite Address Country"}
        ),
    )
    fav_adresse_city = forms.CharField(
        label=_("Favorite Address City"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Favorite Address City"}
        ),
    )
    fav_adresse_zip = forms.CharField(
        label=_("Favorite Address Zip"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Favorite Address Zip"}
        ),
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password Confirmation"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "name",
            "first_name",
            "allergies_type",
            "fav_adresse",
            "fav_adresse_country",
            "fav_adresse_city",
            "fav_adresse_zip",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New Password"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm New Password"}
        ),
        label="Confirm New Password",
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Old Password"}
        ),
        label="Old Password",
    )
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New Password"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm New Password"}
        ),
        label="Confirm New Password",
    )
