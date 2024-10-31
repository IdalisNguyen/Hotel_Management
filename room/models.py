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
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    phone = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    email = models.EmailField()  # Required email field
    message = models.TextField(blank=True, null=True)  # Optional message
    guests = models.IntegerField(default=1)  # Number of guests
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Subtotal price for the booking

    def save(self, *args, **kwargs):
        # Auto-assign email from user if not provided
        if self.user and not self.email:
            self.email = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user} for room {self.room} from {self.date_start} to {self.date_end} with {self.guests} guests"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    checkin = models.DateField()
    checkout = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    subtotal = models.IntegerField(default=0)  # Thêm trường subtotal để lưu tổng giá cho item này

    def total_booking(self):
        # Tính subtotal dựa trên số lượng khách, số lượng phòng, và giá phòng
        return self.room.price * self.quantity * self.guests

    def save(self, *args, **kwargs):
        # Tự động tính subtotal khi lưu CartItem
        self.subtotal = self.total_booking()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.room.name} - {self.quantity}"