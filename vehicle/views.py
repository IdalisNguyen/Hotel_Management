from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def vehicle(request):
    return render(request,'vehicle.html')
def vehicle_booking(request):
    return render(request,'vehicle_booking.html')


