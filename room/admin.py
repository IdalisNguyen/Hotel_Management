from django.contrib import admin
from .models import Room, RoomBooking, RoomType
# Register your models here.
admin.site.register(Room)
admin.site.register(RoomBooking)
admin.site.register(RoomType)