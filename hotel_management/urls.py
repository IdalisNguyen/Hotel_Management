"""
URL configuration for hotel_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home import views as home
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home.get_home, name='home'),
    path('room/', include(('room.urls', 'room'), namespace='room')),  # Đăng ký namespace 'room'
    path('service/', include(('service.urls', 'service'), namespace='service')),
    path('user', include('user.urls')),
    path('customer', include('customer.urls')),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
