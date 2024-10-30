from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from home import views as home
from .models import UserProfile  # Import the UserProfile model

# Create your views here.
def index(request):
    return render(request,'user.html')
def login(request):
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Retrieve the user from the auth_user table using the email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            # Authenticate the user using the username and password
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None:
                # Log the user in and redirect to the home page
                auth_login(request, authenticated_user)
                return redirect(home.get_home)  # Change 'home' to the appropriate URL name for your home page
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'User with this email does not exist.')

    return render(request, 'login.html')
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')  # Capture the phone number

        # Check for existing username or email
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create a UserProfile with the phone number
            UserProfile.objects.create(user=user, phone=phone)
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to login page after registration

    return render(request, 'register.html')