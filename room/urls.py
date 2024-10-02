from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index1),
    path('/details',views.index)
]
