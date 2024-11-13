from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('<int:roombooking_id>/', views.service, name='service'),
    path('order_food/<int:roombooking_id>/<int:food_id>/', views.order_food, name='order_food'),
    path('delete_food_order/<int:roombooking_id>/<int:order_id>/', views.delete_food_order, name='delete_food_order'),
    path('superuser-page/', views.superuser_page, name='superuser_page'),
    path('vehicle-detail/<int:id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle-detail/<int:id>/book/', views.book_vehicle, name='book_vehicle'),

]
