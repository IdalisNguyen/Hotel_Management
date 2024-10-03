# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_home, name='home'),  # Adjust the URL and view if needed
]
