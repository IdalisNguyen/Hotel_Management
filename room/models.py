# room/models.py
from django.db import models
from django.contrib.auth import get_user_model  # This is to get the custom User model
from django.contrib.auth.models import User

User = get_user_model()

class RoomType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class RoomState(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



class Room(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    state = models.ForeignKey(RoomState, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField(default='No description available')  # Add default value
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # Image field

    def __str__(self):
        return f"{self.name} ({self.state.name})"
    

class RoomBooking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, default=2)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    phone = models.CharField(max_length=15, blank=True, null=True)  # Để trống ban đầu
    email = models.EmailField()  # Email vẫn bắt buộc
    message = models.TextField(blank=True, null=True)  # Optional

    def save(self, *args, **kwargs):
        # Tự động lấy email từ người dùng trước khi lưu
        if self.user:
            self.email = self.user.email  # Lấy email từ User
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user} for room {self.room} from {self.date_start} to {self.date_end}"