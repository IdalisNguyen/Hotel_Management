from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking,CartItem
from django.http import HttpResponse,JsonResponse
from django.contrib import messages


# Create your views here.
def room_details_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo id
    return render(request, 'room_details.html', {'room': room})  

def list_room(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        rooms_in_cart = []
        total_cost = 0

        for item in cart_items:
            room = item.room
            room.checkin_date = item.checkin
            room.checkout_date = item.checkout
            room.guests = item.guests
            room.quantity = item.quantity
            room.total_price = room.price * item.quantity
            rooms_in_cart.append(room)
            total_cost += room.total_price
    else:
        cart = request.session.get('cart', {})
        rooms_in_cart = []
        total_cost = 0

        for room_id, details in cart.items():
            try:
                room = Room.objects.get(id=room_id)
                room.checkin_date = details.get('checkin')
                room.checkout_date = details.get('checkout')
                room.guests = details.get('guests')
                room.quantity = details.get('quantity', 1)
                room.total_price = room.price * room.quantity
                rooms_in_cart.append(room)
                total_cost += room.total_price
            except Room.DoesNotExist:
                pass

    context = {
        'cart_rooms': rooms_in_cart,
        'total_cost': total_cost,
        'cart': {
            'cart_items': rooms_in_cart,
            'total_price': total_cost,
            'item_count': len(rooms_in_cart),
        }
    }

    return render(request, 'room_list.html', context)

@login_required
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = get_object_or_404(Room, id=room_id)
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
        if 'notifications' not in request.session:
            request.session['notifications'] = []

        notifications = request.session['notifications']
        notifications.append(new_notification)
        request.session['notifications'] = notifications

        return redirect('home')

    rooms = Room.objects.all()
    return render(request, 'booking_room.html', {'rooms': rooms})

@login_required
def clear_notifications(request):
    request.session['notifications'] = []  # Xóa tất cả thông báo
    return redirect('home')  # Hoặc điều hướng đến trang mong muốn

def add_to_cart(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.user.is_authenticated:
        # Nếu người dùng đã đăng nhập, lưu vào cơ sở dữ liệu
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            room=room,
            defaults={
                'quantity': 1,
                'checkin': request.POST.get('checkin'),
                'checkout': request.POST.get('checkout'),
                'guests': request.POST.get('guests')
            }
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    else:
        # Nếu người dùng chưa đăng nhập, lưu vào session
        cart = request.session.get('cart', {})
        room_id_str = str(room_id)

        if room_id_str in cart:
            cart[room_id_str]['quantity'] += 1
        else:
            cart[room_id_str] = {
                'quantity': 1,
                'checkin': request.POST.get('checkin'),
                'checkout': request.POST.get('checkout'),
                'guests': request.POST.get('guests')
            }

        request.session['cart'] = cart
        request.session.modified = True

    # Kiểm tra nếu request là AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else len(request.session.get('cart', {}))
        total_price = sum(item.room.price * item.quantity for item in CartItem.objects.filter(user=request.user)) if request.user.is_authenticated else sum(room['quantity'] for room in request.session.get('cart', {}).values())
        return JsonResponse({
            'success': True,
            'cart_count': cart_item_count,
            'total_price': total_price
        })

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_from_cart(request, room_id):
    if request.user.is_authenticated:
        # Nếu người dùng đã đăng nhập, xóa item trong giỏ hàng từ cơ sở dữ liệu
        CartItem.objects.filter(user=request.user, room_id=room_id).delete()
    else:
        # Nếu người dùng chưa đăng nhập, xóa item từ session
        cart = request.session.get('cart', {})
        if str(room_id) in cart:
            del cart[str(room_id)]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', '/'))