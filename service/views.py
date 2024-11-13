from django.shortcuts import render, get_object_or_404, redirect
from room.models import RoomBooking  # Đảm bảo đường dẫn đến model RoomBooking là chính xác
from .models import FoodItem, Vehicle, FoodOrder, VehicleOrder  # Import các model khác
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz
from datetime import datetime

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
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_item = get_object_or_404(FoodItem, id=food_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        quantity = int(request.POST.get('quantity'))
        order_time_str = request.POST.get('order_time')
        special_instructions = request.POST.get('special_instructions')

        # Chuyển đổi order_time từ chuỗi thành datetime dạng timezone-aware
        try:
            order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M')
            order_time = timezone.make_aware(order_time, timezone.get_current_timezone())
        except ValueError:
            return render(request, 'food_order_detail.html', {
                'room_booking': room_booking,
                'food_item': food_item,
                'error_message': "Thời gian đặt món không hợp lệ. Vui lòng thử lại.",
                'order_time': order_time_str
            })

        # Đảm bảo date_start và date_end là timezone-aware
        date_start = room_booking.date_start
        date_end = room_booking.date_end
        if timezone.is_naive(date_start):
            date_start = timezone.make_aware(date_start, timezone.get_current_timezone())
        if timezone.is_naive(date_end):
            date_end = timezone.make_aware(date_end, timezone.get_current_timezone())

        # Kiểm tra xem thời gian order có nằm trong khoảng thời gian đặt phòng không
        if date_start <= order_time <= date_end:
            # Tạo hoặc cập nhật đơn đặt món ăn nếu đã tồn tại
            food_order, created = FoodOrder.objects.get_or_create(
                user=request.user,
                room_booking=room_booking,
                food_item=food_item,
                defaults={
                    'quantity': quantity,
                    'order_time': order_time,
                    'special_instructions': special_instructions
                }
            )

            if not created:
                # Nếu đơn đã tồn tại, cập nhật lại các thông tin của đơn đặt món
                food_order.quantity = quantity
                food_order.order_time = order_time
                food_order.special_instructions = special_instructions
                food_order.save()

            # Tạo thông báo đặt món thành công
            notification_message = f"Món {food_item.name} đã được đặt thành công cho phòng {room_booking.room.name}!"
            request.session['notifications'] = request.session.get('notifications', [])
            request.session['notifications'].append(notification_message)

            # Chuyển hướng đến trang dịch vụ
            return redirect('service:service', roombooking_id=roombooking_id)
        else:
            # Nếu thời gian đặt không hợp lệ
            return render(request, 'food_order_detail.html', {
                'room_booking': room_booking,
                'food_item': food_item,
                'error_message': "Thời điểm đặt món phải nằm trong khoảng thời gian đặt phòng.",
                'order_time': order_time_str
            })

    # Xử lý GET request để hiện form đặt món
    return render(request, 'food_order_detail.html', {
        'room_booking': room_booking,
        'food_item': food_item,
        'order_time': timezone.now().strftime('%Y-%m-%dT%H:%M')  # Hiển thị thời gian mặc định để nhập
    })


        
@login_required
def food_order_detail(request, roombooking_id, food_id):
    # Lấy thông tin đặt phòng và món ăn
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_item = get_object_or_404(FoodItem, id=food_id)
    
    # Truyền dữ liệu vào context
    context = {
        'room_booking': room_booking,
        'food_item': food_item,
    }

    return render(request, 'food_order_detail.html', context)

# def delete_food_order(request, roombooking_id, order_id):
#     # Lấy thông tin RoomBooking và FoodOrder
#     room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
#     food_order = get_object_or_404(FoodOrder, id=order_id, room_booking=room_booking)
    
#     # Trừ tổng giá của FoodOrder khỏi subtotal của RoomBooking
#     room_booking.subtotal -= food_order.total_price
#     room_booking.save()
    
#     # Xóa đơn đặt đồ ăn
#     food_order.delete()
    
#     # Chuyển hướng về trang chi tiết đặt phòng
#     return redirect('room:room_booking_detail', booking_id=roombooking_id)

def delete_food_order(request, roombooking_id, order_id):
    # Lấy thông tin RoomBooking và FoodOrder
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_order = get_object_or_404(FoodOrder, id=order_id, room_booking=room_booking)
    
    # Trừ tổng giá của FoodOrder khỏi subtotal của RoomBooking
    room_booking.subtotal -= food_order.total_price
    room_booking.save()
    
    # Xóa đơn đặt đồ ăn
    food_order.delete()
    
    # Tạo thông báo xóa thành công
    notification_message = f"Đơn đặt món {food_order.food_item.name} đã được xóa thành công."
    request.session['notifications'] = request.session.get('notifications', [])
    request.session['notifications'].append(notification_message)

    # Chuyển hướng về trang dịch vụ của phòng
    return redirect('room:room_booking_detail', booking_id=roombooking_id)

@login_required
def update_food_order(request, roombooking_id, order_id):
    # Lấy thông tin RoomBooking và FoodOrder
    room_booking = get_object_or_404(RoomBooking, id=roombooking_id)
    food_order = get_object_or_404(FoodOrder, id=order_id, room_booking=room_booking)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        quantity = int(request.POST.get('quantity'))
        order_time_str = request.POST.get('order_time')
        special_instructions = request.POST.get('special_instructions')

        # Chuyển đổi order_time từ chuỗi thành datetime dạng timezone-aware
        if order_time_str:
            try:
                order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M')
                order_time = timezone.make_aware(order_time, timezone.get_current_timezone())
            except ValueError:
                return render(request, 'food_order_detail.html', {
                    'room_booking': room_booking,
                    'food_item': food_order.food_item,
                    'order': food_order,
                    'error_message': "Thời gian đặt món không hợp lệ. Vui lòng thử lại."
                })
        else:
            order_time = food_order.order_time  # Giữ nguyên thời gian cũ nếu không có giá trị mới

        # Cập nhật các thông tin của đơn đặt món
        food_order.quantity = quantity
        food_order.order_time = order_time
        food_order.special_instructions = special_instructions

        # Cập nhật lại tổng giá dựa trên số lượng mới
        food_order.total_price = food_order.quantity * food_order.food_item.price

        # Lưu lại đơn đặt món
        food_order.save()

        # Tạo thông báo cập nhật thành công
        notification_message = f"Đơn đặt món {food_order.food_item.name} đã được cập nhật thành công."
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)

        # Chuyển hướng đến trang dịch vụ
        return redirect('service:service', roombooking_id=roombooking_id)
    
    # Nếu request là GET, trả về trang food_order_detail với dữ liệu cũ để sửa
    context = {
        'room_booking': room_booking,
        'food_item': food_order.food_item,
        'order': food_order
    }
    return render(request, 'food_order_detail.html', context)

def order_vehicle(request):
    return (request,"vehicle_details.html")
