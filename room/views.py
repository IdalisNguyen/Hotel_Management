from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking
from django.http import HttpResponse
from django.contrib import messages


# Create your views here.
def room_details_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo id
    return render(request, 'room_details.html', {'room': room})  

def index1(request):
    cart = request.session.get('cart', {})
    rooms_in_cart = Room.objects.filter(id__in=cart.keys())
    total_cost = sum(room.price * cart[str(room.id)] for room in rooms_in_cart)
    return render(request, 'room_list.html', {'rooms': rooms_in_cart, 'total_cost': total_cost})
@login_required
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = Room.objects.get(id=room_id)
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        phone = request.POST.get('tel-61')
        email = request.POST.get('email-330')
        message = request.POST.get('textarea-20')

        # Tạo bản ghi đặt phòng
        RoomBooking.objects.create(
            user=request.user,
            room=room,
            date_start=date_start,
            date_end=date_end,
            phone=phone,
            email=email,
            message=message
        )

        # Thêm thông báo mới vào session
        new_notification = f'Phòng {room.name} đã được đặt thành công từ {date_start} đến {date_end}!'
        
        # Kiểm tra danh sách thông báo hiện có trong session, nếu không có thì tạo mới
        if 'notifications' not in request.session:
            request.session['notifications'] = []

        # Thêm thông báo mới vào danh sách và lưu lại vào session
        notifications = request.session['notifications']
        notifications.append(new_notification)
        request.session['notifications'] = notifications

        return redirect('home')  # Điều hướng về trang home

    rooms = Room.objects.all()
    return render(request, 'booking_room.html', {'rooms': rooms})

@login_required
def clear_notifications(request):
    request.session['notifications'] = []  # Xóa tất cả thông báo
    return redirect('home')  # Hoặc điều hướng đến trang mong muốn

def add_to_cart(request, room_id):
    cart = request.session.get('cart', {})
    cart[room_id] = cart.get(room_id, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True  # Đảm bảo rằng session được lưu lại
    return redirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart(request, room_id):
    # Lấy giỏ hàng từ session
    cart = request.session.get('cart', {})

    # Xóa phòng khỏi giỏ hàng nếu tồn tại
    if str(room_id) in cart:
        del cart[str(room_id)]

    # Cập nhật lại session
    request.session['cart'] = cart
    request.session.modified = True

    # Redirect về trang hiện tại để cập nhật giỏ hàng
    return redirect(request.META.get('HTTP_REFERER', '/'))