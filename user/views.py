from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request,'user.html')
def index1(request):
    return HttpResponse("this is vehicle Details")

