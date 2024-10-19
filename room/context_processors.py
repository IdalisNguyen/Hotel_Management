from .models import Room  # Import model Room hoặc thay thế bằng model của bạn

def cart_context(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    item_count = sum(cart.values())

    for room_id, quantity in cart.items():
        try:
            room = Room.objects.get(id=room_id)
            items.append({
                'id': room.id,  # Thêm 'id' để xác định phòng khi xóa
                'name': room.name,
                'image_url': room.image.url,
                'price': room.price,
                'quantity': quantity,
            })
            total += room.price * quantity
        except Room.DoesNotExist:
            pass

    return {
        'cart': {
            'items': items,
            'total': total,
            'item_count': item_count,
        }
    }