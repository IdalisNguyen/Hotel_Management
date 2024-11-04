from django.db import models
from room.models import Room, RoomBooking
from django.contrib.auth import get_user_model
from django.contrib import admin

User = get_user_model()

class FoodCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='food_items')
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)  # Thêm trường hình ảnh

    def __str__(self):
        return self.name

class FoodOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_time = models.DateTimeField(auto_now_add=True)
    special_instructions = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.0)
    image = models.ImageField(upload_to='food_order_images/', blank=True, null=True)  # Thêm trường hình ảnh vào FoodOrder

    def save(self, *args, **kwargs):
        # Kiểm tra nếu phòng đã được đặt trước khi lưu
        if not RoomBooking.objects.filter(id=self.room_booking.id).exists():
            raise ValueError("Phòng phải được đặt trước khi đặt dịch vụ ăn uống.")
        # Tự động tính tổng giá dựa trên số lượng và giá của món ăn
        self.total_price = self.quantity * self.food_item.price

        # Cập nhật tổng phụ trong RoomBooking tương ứng
        self.room_booking.subtotal += self.total_price
        self.room_booking.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đơn đặt bởi {self.user} cho món {self.food_item.name} trong phòng {self.room_booking.room.name}"
    

    
admin.site.register(FoodCategory)
admin.site.register(FoodItem)
admin.site.register(FoodOrder)