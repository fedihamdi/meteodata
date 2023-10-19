from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'name', 'first_name', 'email', 'password', 'allergies_type',
            'fav_adresse', 'fav_adresse_country', 'fav_adresse_city', 'fav_adresse_zip'
        ]