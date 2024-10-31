from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.vehicle),
    path('vehicle_details/',views.vehicle_booking)
]
