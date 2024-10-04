# room/models.py
from django.db import models
from django.contrib.auth import get_user_model  # This is to get the custom User model

class RoomType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Room(models.Model):
    name = models.CharField(max_length=255)
    type = models.IntegerField()  # 1 for available, 0 for booked
    state = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField(default='No description available')  # Add default value
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # Image field

    def __str__(self):
        return f"{self.name} ({self.state.name})"
    

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, default=2)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return f"Booking of {self.room.name} by {self.user.username} from {self.date_start} to {self.date_end}"