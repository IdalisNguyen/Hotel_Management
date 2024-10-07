from django.shortcuts import render
from room.models import Room  # Import your Room model

# Create your views here.
def get_home(request):
    rooms = Room.objects.all()  # Fetch all room instances
    context = {
        'rooms': rooms,  # Pass the rooms data to the template
    }
    return render(request, "content.html", context)
def home(request):
    rooms = Room.objects.all()  # Retrieve all room data from the database
    context = {
        'rooms': rooms,  # Pass the room data to the template
        'user': request.user  # This will be the logged-in user
    }
    return render(request, 'content.html', context)


