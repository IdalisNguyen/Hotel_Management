from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:roombooking_id>/', views.service, name='service'),
    path('order_food/<int:roombooking_id>/<int:food_id>/', views.order_food, name='order_food'),
    path('delete_food_order/<int:roombooking_id>/<int:order_id>/', views.delete_food_order, name='delete_food_order'),
    path('food_order_detail/<int:roombooking_id>/<int:food_id>/', views.food_order_detail, name='food_order_detail'),
    path('update_food_order/<int:roombooking_id>/<int:order_id>/', views.update_food_order, name='update_food_order'),
]
