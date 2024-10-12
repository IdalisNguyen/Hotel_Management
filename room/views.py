from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from room.models import Room, RoomBooking
from django.http import HttpResponse

# Create your views here.
def room_details_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)  # Lấy phòng theo id
    return render(request, 'room_details.html', {'room': room})  
def index1(request):
    return render(request,'room_list.html')

@login_required(login_url='/login/')  # Yêu cầu người dùng đăng nhập để đặt phòng
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')  # Lấy ID của phòng từ form
        date_start = request.POST.get('date_start')  # Lấy ngày bắt đầu
        date_end = request.POST.get('date_end')  # Lấy ngày kết thúc

        room = Room.objects.get(id=room_id)  # Lấy thông tin phòng từ ID

        # Tạo bản ghi RoomBooking mới
        booking = RoomBooking.objects.create(
            room=room,
            user=request.user,  # Gán người dùng hiện tại
            date_start=date_start,
            date_end=date_end
        )
        booking.save()
        return redirect('home')  # Chuyển hướng về trang chủ sau khi đặt phòng thành công

    rooms = Room.objects.all()  # Lấy danh sách phòng để hiển thị trong form
    context = {
        'rooms': rooms
    }
    return render(request, 'booking_room.html', context)