from django.db import models
from django.contrib.auth.models import AbstractUser
class UserProfile(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store the hashed password
    allergies_type = models.CharField(max_length=100, null=True, blank=True)  # list of elements
    fav_adresse = models.CharField(max_length=200, null=True, blank=True)
    fav_adresse_country = models.CharField(max_length=50, null=True, blank=True)
    fav_adresse_city = models.CharField(max_length=50, null=True, blank=True)
    fav_adresse_zip = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username  # You can use a different field for representation
# 1- python manage.py makemigrations
# 2- manage.py migrate
