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
    return render(request,'room_list.html')

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

        RoomBooking.objects.create(
            user=request.user,
            room=room,
            date_start=date_start,
            date_end=date_end,
            phone=phone,
            email=email,
            message=message
        )

        messages.success(request, 'Phòng của bạn đã được đặt thành công!')
        return redirect('home')  # Điều hướng về trang chủ sau khi đặt phòng thành công

    rooms = Room.objects.all()
    return render(request, 'booking_room.html', {'rooms': rooms})