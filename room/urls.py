from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index1,name="list_room"),
    path('/details',views.index)
]
