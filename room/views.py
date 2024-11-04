from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking, CartItem
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from datetime import datetime 
from django.utils import timezone

# Xem chi tiết phòng
def room_details_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo ID
    return render(request, 'room_details.html', {'room': room})  

# Hiển thị danh sách phòng và giỏ hàng
def list_room(request):
    cart_items = []
    total_price = 0
    item_count = 0

    if request.user.is_authenticated:
        # Nếu người dùng đã đăng nhập, lấy giỏ hàng từ cơ sở dữ liệu
        cart_items_db = CartItem.objects.filter(user=request.user)
        for item in cart_items_db:
            room = item.room
            
            # Tính số ngày giữa checkin và checkout
            num_days = (item.checkout - item.checkin).days
            if num_days < 1:  # Mặc định ít nhất là 1 ngày nếu checkout < checkin
                num_days = 1

            # Tính tổng giá cho mục này với số ngày
            item_total_price = item.subtotal * num_days
            total_price += item_total_price
            item_count += item.quantity
            
            # Thêm thông tin vào danh sách cart_items
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
        # Nếu người dùng chưa đăng nhập, lấy giỏ hàng từ session
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
                    num_days = 1  # Mặc định là 1 ngày nếu thiếu ngày

                # Tính tổng giá cho mục này với số ngày
                item_total_price = room.price * quantity * guests * num_days
                total_price += item_total_price
                item_count += quantity
                
                # Thêm thông tin vào danh sách cart_items
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

# Đặt phòng
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
        new_notification = f'Phòng {room.name} đã được đặt thành công từ {date_start} đến {date_end}, Nhân viên hỗ trợ bên khách sạn sẽ liên hệ lại với bạn ngay lập tức!!!'
        if 'notifications' not in request.session:
            request.session['notifications'] = []

        notifications = request.session['notifications']
        notifications.append(new_notification)
        request.session['notifications'] = notifications

        return redirect('home')

    rooms = Room.objects.all()
    return render(request, 'booking_room.html', {'rooms': rooms})

# Xóa thông báo
@login_required
def clear_notifications(request):
    request.session['notifications'] = []  # Xóa tất cả thông báo
    return redirect('home')  # Hoặc điều hướng đến trang mong muốn

# Thêm phòng vào giỏ hàng
def add_to_cart(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Kiểm tra trạng thái phòng
    if room.state_id == 2:
        notification_message = f'Không thể thêm {room.name} vì trạng thái không sẵn sàng!'
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)
        messages.error(request, f"Phòng {room.name} hiện không khả dụng để đặt. Vui lòng chọn phòng khác.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

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

        # Tính subtotal cho mục này
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

    # Cập nhật trạng thái phòng thành "Không sẵn sàng" (state_id = 2)
    room.state_id = 2
    room.save()

    # Kiểm tra nếu request là AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else len(request.session.get('cart', {}))
        total_price = sum(item.room.price * item.quantity * item.guests for item in CartItem.objects.filter(user=request.user)) if request.user.is_authenticated else sum(room['quantity'] for room in request.session.get('cart', {}).values())
        return JsonResponse({
            'success': True,
            'cart_count': cart_item_count,
            'total_price': total_price,
            'item_total_price': cart_item.subtotal if request.user.is_authenticated else 0
        })

    # Thêm thông báo thành công khi phòng sẵn sàng để đặt
    messages.success(request, f"Phòng {room.name} đã được thêm vào giỏ hàng của bạn thành công.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Xóa phòng khỏi giỏ hàng
@login_required
def remove_from_cart(request, room_id,n):
    room = get_object_or_404(Room, id=room_id)
    
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

    # Cập nhật trạng thái phòng thành "Sẵn sàng" (state_id = 1)
    if n == 1:
        room.state_id = 1
    elif n ==2 :
        room.state_id = 2

    room.save()

    messages.info(request, f"Phòng {room.name} đã được xóa khỏi giỏ hàng.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

# @login_required
# def state_booking(request, room_id):
#     room = get_object_or_404(Room, id=room_id)
    
#     if request.user.is_authenticated:
#         # Nếu người dùng đã đăng nhập, xóa item trong giỏ hàng từ cơ sở dữ liệu
#         CartItem.objects.filter(user=request.user, room_id=room_id).delete()
#     else:
#         # Nếu người dùng chưa đăng nhập, xóa item từ session
#         cart = request.session.get('cart', {})
#         if str(room_id) in cart:
#             del cart[str(room_id)]
#         request.session['cart'] = cart
#         request.session.modified = True

#     # Cập nhật trạng thái phòng thành "Sẵn sàng" (state_id = 1)
#     room.state_id = 3
#     room.save()

#     # messages.info(request, f"Phòng {room.name} đã được xóa khỏi giỏ hàng.")
#     return redirect(request.META.get('HTTP_REFERER', '/'))
# # Gửi đơn hàng đặt phòng


@login_required
def submit_order(request):
    if request.method == 'POST':
        user = request.user
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        # Lấy dữ liệu phòng cụ thể từ form đã gửi
        room_id = request.POST.get('room_id')
        checkin_date_str = request.POST.get('checkin_date')
        checkout_date_str = request.POST.get('checkout_date')
        guests = int(request.POST.get('guests', 1))  # Mặc định là 1 khách nếu không có
        subtotal = float(request.POST.get('total', 0.0))  # Mặc định subtotal nếu không có
            
        # Chuyển đổi ngày checkin và checkout sang định dạng datetime hợp lệ
        checkin_date = datetime.strptime(checkin_date_str, '%b. %d, %Y')  # Ví dụ định dạng: 'Oct. 30, 2024'
        checkout_date = datetime.strptime(checkout_date_str, '%b. %d, %Y')

        # Lấy phòng và đảm bảo phòng tồn tại
        room = get_object_or_404(Room, id=room_id)

        # Tạo đơn đặt cho phòng cụ thể này
        booking = RoomBooking.objects.create(
            user=user,
            room=room,
            date_start=timezone.make_aware(checkin_date),
            date_end=timezone.make_aware(checkout_date),
            phone=phone,
            email=email,
            guests=guests,
            subtotal=subtotal,
            image=room.image
            
        )

        # Thêm thông báo cho phòng đã đặt
        notification_message = f'Phòng {room.name} đã được đặt thành công từ {checkin_date_str} đến {checkout_date_str}!'
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)

        # Xóa phòng này khỏi giỏ hàng sau khi đặt
        remove_from_cart(request, room_id,2)

        # Lưu thông báo vào session
        request.session.modified = True
        messages.success(request, "Your booking has been confirmed!")

        return redirect('home')  # Điều hướng về trang chủ hoặc trang xác nhận đặt phòng

    return redirect('cart')  # Điều hướng về giỏ hàng nếu yêu cầu không phải là POST


# Xác nhận đặt phòng
@login_required  # đảm bảo chỉ người dùng đã đăng nhập mới có thể truy cập
def room_booked(request):
    # Lấy tất cả thông tin phòng đã đặt của người dùng đang đăng nhập
    bookings = RoomBooking.objects.filter(user=request.user)
    
    # Truyền thông tin phòng đã đặt vào template
    return render(request, "room_booked.html", {"bookings": bookings})