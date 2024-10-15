from django.contrib import admin
from django.urls import path,include
from . import views
from .views import room_details_view,clear_notifications

urlpatterns = [
    path('',views.index1,name="list_room"),
    path('room/<int:room_id>/', room_details_view, name='room_details'),  # Đường dẫn cho trang chi tiết phòng
    path('/booking', views.book_room, name='book_room'),  # Đường dẫn đến trang booking
    path('clear_notifications/', clear_notifications, name='clear_notifications')

]
