from django.db import models
from room.models import RoomBooking 
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()

# Các model liên quan đến đồ ăn
class FoodCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='food_items')
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    status = models.CharField(max_length=50, default='sẵn sàng')

    def __str__(self):
        return self.name

# Model cho danh mục phương tiện
class VehicleCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Model cho phương tiện
class Vehicle(models.Model):
    type = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField()
    available = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, related_name='vehicles')
    image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    status = models.CharField(max_length=50, default='sẵn sàng')
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Giá thuê theo ngày
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2, default=2.0)  # Giá thuê theo giờ


    def __str__(self):
        return f"{self.type} - {self.license_plate}"

# Model cho đơn đặt đồ ăn
class FoodOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE, related_name='food_orders')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_time = models.DateTimeField(auto_now_add=True)
    special_instructions = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.0)
    image = models.ImageField(upload_to='food_order_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        request = kwargs.get('request')  # Lấy request từ view

        # Kiểm tra thời điểm đặt món trong khoảng thời gian đặt phòng
        if self.room_booking.date_start <= timezone.now() <= self.room_booking.date_end:
            # Tính tổng giá dựa trên số lượng và giá của món ăn
            self.total_price = self.quantity * self.food_item.price
            # Cập nhật tổng giá tiền của RoomBooking
            self.room_booking.subtotal += self.total_price
            self.room_booking.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Thời điểm đặt món phải nằm trong khoảng thời gian đặt phòng.")

    def __str__(self):
        return f"Đơn đặt bởi {self.user} cho món {self.food_item.name} trong phòng {self.room_booking.room.name}"
    
# Model cho đơn đặt phương tiện
class VehicleOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE, related_name='vehicle_orders')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    rental_time = models.DateTimeField()
    return_time = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.0)  # Tổng chi phí

    def save(self, *args, **kwargs):
        # Tính tổng chi phí dựa trên số ngày thuê và giá thuê theo ngày
        rental_days = (self.return_time - self.rental_time).days
        self.total_cost = rental_days * self.vehicle.daily_rate
        # Cập nhật tổng giá tiền của RoomBooking
        self.room_booking.subtotal += self.total_cost
        self.room_booking.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đơn đặt xe bởi {self.user} cho phương tiện {self.vehicle.type}"

# Đăng ký model vào admin
admin.site.register(FoodCategory)
admin.site.register(FoodItem)
admin.site.register(FoodOrder)
admin.site.register(VehicleCategory)
admin.site.register(Vehicle)
admin.site.register(VehicleOrder)