from room.models import Room, CartItem

def cart_context(request):
    cart_items = []
    total_price = 0
    item_count = 0

    if request.user.is_authenticated:
        # Lấy giỏ hàng từ cơ sở dữ liệu nếu người dùng đã đăng nhập
        cart_items_db = CartItem.objects.filter(user=request.user)
        for item in cart_items_db:
            total_price += item.room.price * item.quantity
            item_count += item.quantity
            cart_items.append({
                'id': item.room.id,
                'name': item.room.name,
                'image_url': item.room.image.url if item.room.image else '',
                'price': item.room.price,
                'quantity': item.quantity,
                'total': item.room.price * item.quantity,
            })
    else:
        # Lấy giỏ hàng từ session nếu người dùng chưa đăng nhập
        cart = request.session.get('cart', {})
        for room_id, details in cart.items():
            try:
                room = Room.objects.get(id=room_id)
                quantity = details.get('quantity', 1)
                total_price += room.price * quantity
                item_count += quantity
                cart_items.append({
                    'id': room.id,
                    'name': room.name,
                    'image_url': room.image.url if room.image else '',
                    'price': room.price,
                    'quantity': quantity,
                    'total': room.price * quantity,
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