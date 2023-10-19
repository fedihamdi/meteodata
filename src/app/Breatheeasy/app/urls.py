from django.urls import path
from . import views

urlpatterns = [
    path('create_profile/', views.user_profile_create, name='create_profile'),
]
