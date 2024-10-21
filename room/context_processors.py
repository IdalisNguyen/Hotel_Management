from .models import Room

def cart_context(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    item_count = 0  # Biến để đếm tổng số lượng phòng trong giỏ hàng

    for room_id, details in cart.items():
        try:
            room = Room.objects.get(id=room_id)
            # Nếu 'details' là int, sử dụng giá trị này như số lượng
            if isinstance(details, int):
                quantity = details
            else:
                quantity = details.get('quantity', 1)  # Mặc định là 1 nếu không có 'quantity'

            item_total = room.price * quantity
            total_price += item_total
            item_count += quantity  # Cộng dồn số lượng phòng vào biến item_count

            cart_items.append({
                'id': room.id,
                'name': room.name,
                'image_url': room.image.url,
                'price': room.price,
                'quantity': quantity,
                'total': item_total
            })
        except Room.DoesNotExist:
            pass

    return {
        'cart': {
            'cart_items': cart_items,
            'total_price': total_price,
            'item_count': item_count  # Tổng số lượng phòng trong giỏ hàng
        }
    }
