from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking, CartItem, RoomState
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from datetime import datetime 
from django.utils import timezone
from service.models import FoodOrder  # Import đúng model FoodOrder từ ứng dụng service
from datetime import timedelta

# Xem chi tiết phòng
# def room_details_view(request, room_id):
#     room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo ID
#     return render(request, 'room_details.html', {'room': room})  

def room_details_view(request, room_id):
    # Retrieve the room object
    room = get_object_or_404(Room, id=room_id)
    
    # Retrieve bookings for the specified room
    bookings = RoomBooking.objects.filter(room=room)

#     # Collect all booked dates for this room in DD/MM/YYYY format
    booked_dates = []
    for booking in bookings:
        current_date = booking.date_start.date()  # Start date as a date object
        end_date = booking.date_end.date()  # End date as a date object
        
        # Loop through each date in the booking range and add to booked_dates
        while current_date <= end_date:
            booked_dates.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)

#     # Check today's date
#     today = datetime.now().date()
#     today_formatted = today.strftime('%d/%m/%Y')

#     # Retrieve RoomState instances based on IDs
#     state_available = get_object_or_404(RoomState, id=1)  # 1 = Sẵn sàng
#     state_booked = get_object_or_404(RoomState, id=3)    # 3 = Đang được đặt
#     # print(booked_dates)
#     # Update room state based on today's booking status
#     if today_formatted in booked_dates:
#         room.state = state_booked  # Assign the RoomState instance for "Currently Booked"
#         # print(state_booked)
#     else:
#         room.state = state_available  # Assign the RoomState instance for "Available"
# #        print(state_available)
    
    # Save updated room state to the database
    room.save()

    # Print booked dates for debugging
    # print("Booked dates:", booked_dates)

    # Pass the room and booked dates to the template context
    context = {
        'room': room,
        'booked_dates': booked_dates,  # Pass booked dates in 'DD/MM/YYYY' format
    }
    return render(request, 'room_details.html', context)
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

    # Check room availability status
    if room.state_id == 2:
        notification_message = f'Không thể thêm {room.name} vì trạng thái không sẵn sàng!'
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)
        messages.error(request, f"Phòng {room.name} hiện không khả dụng để đặt. Vui lòng chọn phòng khác.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if room.state_id == 3:
        notification_message = f'Không thể thêm {room.name} vì trạng thái đang được đặt!'
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)
        messages.error(request, f"Phòng {room.name} hiện không khả dụng để đặt. Vui lòng chọn phòng khác.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.user.is_authenticated:
        # Create a new cart item for each submission instead of updating quantity
        cart_item = CartItem.objects.create(
            user=request.user,
            room=room,
            quantity=1,
            checkin=request.POST.get('checkin'),
            checkout=request.POST.get('checkout'),
            guests=int(request.POST.get('guests', 1)),
            subtotal=room.price * int(request.POST.get('guests', 1))
        )

    else:
        # If the user is not logged in, save each new order in session
        cart = request.session.get('cart', {})
        room_id_str = str(room_id)

        # Add a unique key for each item based on timestamp or unique identifier to avoid updates
        unique_key = f"{room_id_str}_{len(cart) + 1}"  # Or use a UUID for more uniqueness
        cart[unique_key] = {
            'quantity': 1,
            'checkin': request.POST.get('checkin'),
            'checkout': request.POST.get('checkout'),
            'guests': int(request.POST.get('guests', 1)),
            'subtotal': room.price * int(request.POST.get('guests', 1))
        }

        # Update session
        request.session['cart'] = cart
        request.session.modified = True

    # Update room status to "Unavailable" (state_id = 2)
    room.save()

    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else len(request.session.get('cart', {}))
        total_price = sum(item.subtotal for item in CartItem.objects.filter(user=request.user)) if request.user.is_authenticated else sum(item['subtotal'] for item in request.session.get('cart', {}).values())
        return JsonResponse({
            'success': True,
            'cart_count': cart_item_count,
            'total_price': total_price,
            'item_total_price': cart_item.subtotal if request.user.is_authenticated else 0
        })

    # Add a success message for adding room to the cart
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
    elif n == 2 :
        room.state_id = 2
    elif n == 3 :
        room.state_id = 3

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

        # Retrieve specific room data from the submitted form
        room_id = request.POST.get('room_id')
        checkin_date_str = request.POST.get('checkin_date')
        checkout_date_str = request.POST.get('checkout_date')
        guests = int(request.POST.get('guests', 1))  # Default to 1 guest if not provided
        subtotal = float(request.POST.get('total', 0.0))  # Default subtotal if not provided
        idd_card = int(request.POST.get('idd_card'))

        # Convert check-in and check-out dates to valid datetime format
        checkin_date = datetime.strptime(checkin_date_str, '%b. %d, %Y')  # Example format: 'Oct. 30, 2024'
        checkout_date = datetime.strptime(checkout_date_str, '%b. %d, %Y')

        # Get the room and ensure it exists
        room = get_object_or_404(Room, id=room_id)
        bookings = RoomBooking.objects.filter(room=room)

        # Collect all booked dates for this room in DD/MM/YYYY format
        booked_dates = set()  # Use a set for faster lookups
        for booking in bookings:
            current_date = booking.date_start.date()
            end_date = booking.date_end.date()
            while current_date <= end_date:
                booked_dates.add(current_date.strftime('%d/%m/%Y'))
                current_date += timedelta(days=1)

        # Check if requested dates overlap with booked dates
        current_date = checkin_date
        while current_date <= checkout_date:
            if current_date.strftime('%d/%m/%Y') in booked_dates:
                notification_message = f'Không thể thêm {room.name} vì đang được đặt!'
                request.session['notifications'] = request.session.get('notifications', [])
                request.session['notifications'].append(notification_message)
                messages.error(request, f"Phòng {room.name} hiện không khả dụng để đặt. Vui lòng chọn phòng khác.")
                return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page
            current_date += timedelta(days=1)

        # If dates are available, create the booking
        booking = RoomBooking.objects.create(
            user=user,
            room=room,
            date_start=timezone.make_aware(checkin_date),
            date_end=timezone.make_aware(checkout_date),
            phone=phone,
            email=email,
            guests=guests,
            subtotal=subtotal,
            image=room.image,
            identity_card=idd_card
        )

        # Add a notification for the booked room
        notification_message = f'Phòng {room.name} đã được đặt thành công từ {checkin_date_str} đến {checkout_date_str}!'
        request.session['notifications'] = request.session.get('notifications', [])
        request.session['notifications'].append(notification_message)

        # Update the room state
        # room.state = 3  # Assuming 3 indicates booked
        room.save()

        # Remove the room from the cart after booking
        remove_from_cart(request, room_id, 1)

        # Save notifications in session
        request.session.modified = True
        messages.success(request, "Your booking has been confirmed!")

        return redirect('home')  # Redirect to home or booking confirmation page

    return redirect('cart')  # Redirect to cart if the request is not POST

# Xác nhận đặt phòng
@login_required  # đảm bảo chỉ người dùng đã đăng nhập mới có thể truy cập
def room_booked(request):
    # Lấy tất cả thông tin phòng đã đặt của người dùng đang đăng nhập
    bookings = RoomBooking.objects.filter(user=request.user)
    
    # Truyền thông tin phòng đã đặt vào template
    return render(request, "room_booked.html", {"bookings": bookings})


def room_booking_detail(request, booking_id):
    # Lấy thông tin đặt phòng
    booking = get_object_or_404(RoomBooking, id=booking_id)
    
    # Lấy tất cả các đơn đặt đồ ăn liên quan đến RoomBooking này
    food_orders = booking.food_orders.all()  # Sử dụng related_name='food_orders' để truy cập các FoodOrder liên quan
    
    # Truyền booking và food_orders vào template
    return render(request, 'room_booked_details.html', {
        'booking': booking,
        'food_orders': food_orders,
    })