# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_home, name='home'),  # Sử dụng hàm get_home cho route '/'
]