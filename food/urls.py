from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.foods,name="food"),
    path('food_details',views.index1)
]
