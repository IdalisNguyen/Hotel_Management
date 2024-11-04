from django.shortcuts import render
from django.http import HttpResponse
from .models import FoodItem

# Create your views here.
def foods(request):
    food_items = FoodItem.objects.all()
    return render(request, 'food.html', {'food_items': food_items})# def index1(request):
#     return HttpResponse("this is food Details")
def index1(request):
    return render(request,'food_details.html')

