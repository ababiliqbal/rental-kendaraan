# rental_project/urls.py
from django.contrib import admin
from django.urls import path
from rental_app import views

from django.conf import settings
from django.conf.urls.static import static 


urlpatterns = [
    path('', views.home, name='home'), 
    path('admin/', admin.site.urls),
    path('register/', views.register_pelanggan, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)