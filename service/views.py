from django.shortcuts import render, get_object_or_404,redirect
from room.models import RoomBooking  # Đảm bảo đường dẫn đến model RoomBooking là chính xác
from .models import FoodItem, Vehicle,FoodOrder,VehicleOrder  # Import các model khác
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Vehicle
from django.http import JsonResponse

def service(request, roombooking_id):
    # Lấy thông tin phòng dựa trên roombooking_id
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_items = FoodItem.objects.all()
    vehicles = Vehicle.objects.all()
    
    # Truyền dữ liệu vào ngữ cảnh
    return render(request, 'home_service.html', {
        'roombooking_id': roombooking_id,  # Truyền roombooking_id vào ngữ cảnh
        'booking': room_booking,
        'food_items': food_items,
        'vehicles': vehicles,
    })
@login_required
def order_food(request, roombooking_id, food_id):
    # Lấy thông tin phòng và món ăn
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_item = get_object_or_404(FoodItem, id=food_id)
    
    # Tạo đơn đặt món ăn với số lượng mặc định là 1
    food_order = FoodOrder(
        user=request.user,
        room_booking=room_booking,
        food_item=food_item,
        quantity=1,
    )
    food_order.save()  # Lưu đơn hàng
    
    # Tạo thông báo đặt món thành công
    notification_message = f"Món {food_item.name} đã được đặt thành công cho phòng {room_booking.room.name}!"
    request.session['notifications'] = request.session.get('notifications', [])
    request.session['notifications'].append(notification_message)
    
    # Chuyển hướng đến room_booking_detail trong app 'room'
    return redirect('service:service', roombooking_id=roombooking_id)




def delete_food_order(request, roombooking_id, order_id):
    # Lấy thông tin RoomBooking và FoodOrder
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_order = get_object_or_404(FoodOrder, id=order_id, room_booking=room_booking)
    
    # Trừ tổng giá của FoodOrder khỏi subtotal của RoomBooking
    room_booking.subtotal -= food_order.total_price
    room_booking.save()
    
    # Xóa đơn đặt đồ ăn
    food_order.delete()
    
    # Chuyển hướng về trang chi tiết đặt phòng
    return redirect('room:room_booking_detail', booking_id=roombooking_id)

@user_passes_test(lambda u: u.is_superuser)
def superuser_page(request):
    return render(request, 'superuser_page.html')

def vehicle_detail(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)
    booking = RoomBooking.objects.filter(user=request.user).order_by('-date_start').first()
    return render(request, 'vehicle_detail.html', {'vehicle': vehicle, 'booking': booking})
    # return render(request, 'vehicle_detail.html', {'vehicle': vehicle})

@login_required
def book_vehicle(request, id):
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, id=id)
        rental_time = request.POST.get('rental_time')
        return_time = request.POST.get('return_time')

        # Tạo đơn đặt xe
        vehicle_order = VehicleOrder.objects.create(
            user=request.user,
            vehicle=vehicle,
            rental_time=rental_time,
            return_time=return_time
        )

        # Trả về phản hồi JSON
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})