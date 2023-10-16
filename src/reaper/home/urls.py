from django.urls import path

from . import views

urlpatterns = [
    #path('', views.estimation_data_view, name='index'),
    path('', views.pollen_data_view, name='index'),
]
