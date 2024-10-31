from room.models import Room, CartItem
from datetime import datetime

def cart_context(request):
    cart_items = []
    total_price = 0
    item_count = 0

    if request.user.is_authenticated:
        # Lấy giỏ hàng từ cơ sở dữ liệu nếu người dùng đã đăng nhập
        cart_items_db = CartItem.objects.filter(user=request.user)
        for item in cart_items_db:
            # Tính số ngày giữa checkin và checkout
            num_days = (item.checkout - item.checkin).days
            if num_days < 1:
                num_days = 1  # Đặt mặc định là 1 ngày nếu checkout <= checkin

            # Tính tổng giá cho item này với số ngày
            item_total_price = item.room.price * item.quantity * item.guests * num_days
            total_price += item_total_price
            item_count += item.quantity

            cart_items.append({
                'id': item.room.id,
                'name': item.room.name,
                'image_url': item.room.image.url if item.room.image else '',
                'price': item.room.price,
                'quantity': item.quantity,
                'guests': item.guests,
                'checkin_date': item.checkin,
                'checkout_date': item.checkout,
                'num_days': num_days,  # Số ngày lưu trú
                'total': item_total_price,  # Tổng giá trị với số ngày đã tính
            })
    else:
        # Lấy giỏ hàng từ session nếu người dùng chưa đăng nhập
        cart = request.session.get('cart', {})
        for room_id, details in cart.items():
            try:
                room = Room.objects.get(id=room_id)
                quantity = details.get('quantity', 1)
                guests = details.get('guests', 1)
                checkin_date = details.get('checkin_date')
                checkout_date = details.get('checkout_date')

                # Tính số ngày giữa checkin và checkout
                if checkin_date and checkout_date:
                    checkin_date_obj = datetime.strptime(checkin_date, '%Y-%m-%d').date()
                    checkout_date_obj = datetime.strptime(checkout_date, '%Y-%m-%d').date()
                    num_days = (checkout_date_obj - checkin_date_obj).days
                    if num_days < 1:
                        num_days = 1
                else:
                    num_days = 1  # Mặc định là 1 ngày nếu thiếu ngày

                # Tính tổng giá cho item này với số ngày
                item_total_price = room.price * quantity * guests * num_days
                total_price += item_total_price
                item_count += quantity

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
                    'total': item_total_price,  # Tổng giá trị với số ngày đã tính
                })
            except Room.DoesNotExist:
                continue

    return {
        'cart': {
            'cart_items': cart_items,
            'total_price': total_price,
            'item_count': item_count
        }
    }
