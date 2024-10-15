from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request,'food.html')
# def index1(request):
#     return HttpResponse("this is food Details")
def index1(request):
    return render(request,'food_details.html')

