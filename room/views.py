from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking,CartItem
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from datetime import timedelta
import datetime

# Create your views here.
def room_details_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo id
    return render(request, 'room_details.html', {'room': room})  

def list_room(request):
    cart_items = []
    total_price = 0
    item_count = 0

    if request.user.is_authenticated:
        # Lấy giỏ hàng từ cơ sở dữ liệu nếu người dùng đã đăng nhập
        cart_items_db = CartItem.objects.filter(user=request.user)
        for item in cart_items_db:
            room = item.room
            
            # Tính số ngày giữa checkin và checkout
            num_days = (item.checkout - item.checkin).days
            if num_days < 1:  # Trường hợp checkout < checkin, mặc định ít nhất 1 ngày
                num_days = 1

            # Tính tổng giá cho item này với số ngày
            item_total_price = item.subtotal * num_days
            total_price += item_total_price
            item_count += item.quantity
            
            # Thêm thông tin vào cart_items
            cart_items.append({
                'id': room.id,
                'name': room.name,
                'image_url': room.image.url if room.image else '',
                'price': room.price,
                'quantity': item.quantity,
                'guests': item.guests,
                'checkin_date': item.checkin,
                'checkout_date': item.checkout,
                'num_days': num_days,  # Số ngày lưu trú
                'total': item_total_price,  # Tổng giá với số ngày đã tính
            })
    else:
        # Lấy giỏ hàng từ session nếu người dùng chưa đăng nhập
        cart = request.session.get('cart', {})
        for room_id, details in cart.items():
            try:
                room = Room.objects.get(id=room_id)
                quantity = details.get('quantity', 1)
                guests = details.get('guests', 1)
                checkin_date = details.get('checkin')
                checkout_date = details.get('checkout')
                
                # Tính số ngày giữa checkin và checkout
                if checkin_date and checkout_date:
                    checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
                    checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()
                    num_days = (checkout_date - checkin_date).days
                    if num_days < 1:
                        num_days = 1
                else:
                    num_days = 1  # Nếu thiếu ngày thì mặc định là 1 ngày

                # Tính tổng giá cho item này với số ngày
                item_total_price = room.price * quantity * guests * num_days
                total_price += item_total_price
                item_count += quantity
                
                # Thêm thông tin vào cart_items
                cart_items.append({
                    'id': room.id,
                    'name': room.name,
                    'image_url': room.image.url if room.image else '',
                    'price': room.price,
                    'quantity': quantity,
                    'guests': guests,
                    'checkin_date': checkin_date,
                    'checkout_date': checkout_date,
                    'num_days': num_days,  # Số ngày lưu trú
                    'total': item_total_price,  # Tổng giá với số ngày đã tính
                })
            except Room.DoesNotExist:
                continue

    context = {
        'cart_rooms': cart_items,
        'total_cost': total_price,
        'cart': {
            'cart_items': cart_items,
            'total_price': total_price,
            'item_count': item_count,
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
                'guests': int(request.POST.get('guests', 1))
            }
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Tính subtotal cho item này
        cart_item.subtotal = cart_item.room.price * cart_item.quantity * cart_item.guests
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
                'guests': int(request.POST.get('guests', 1))
            }

        # Cập nhật session
        request.session['cart'] = cart
        request.session.modified = True

    # Kiểm tra nếu request là AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else len(request.session.get('cart', {}))
        total_price = sum(item.room.price * item.quantity * item.guests for item in CartItem.objects.filter(user=request.user)) if request.user.is_authenticated else sum(room['quantity'] for room in request.session.get('cart', {}).values())
        return JsonResponse({
            'success': True,
            'cart_count': cart_item_count,
            'total_price': total_price,
            'item_total_price': cart_item.subtotal  # Trả về subtotal đã lưu trong CartItem
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

def room_booked(request):
    return render(request, "room_booked.html")
