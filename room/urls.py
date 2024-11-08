# room/urls.py
from django.urls import path
from . import views
from .views import room_details_view, clear_notifications

urlpatterns = [
    path('list_room/', views.list_room, name="list_room"),
    path('room/<int:room_id>/', room_details_view, name='room_details'),
    path('booking', views.book_room, name='book_room'),
    path('clear_notifications/', clear_notifications, name='clear_notifications'),
    path('add-to-cart/<int:room_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:room_id>/<int:n>/', views.remove_from_cart, name='remove_from_cart'),
    path('room_booked/', views.room_booked, name="room_booked"),
    path('room_booked/<int:booking_id>/', views.room_booking_detail, name='room_booking_detail'),
    path('submit_order/', views.submit_order, name='submit_order'),
]
