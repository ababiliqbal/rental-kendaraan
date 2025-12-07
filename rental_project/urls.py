from django.contrib import admin
from django.urls import path
from manajemen_pengguna import views  # <--- GANTI rental_app JADI manajemen_pengguna
from django.conf import settings
from django.conf.urls.static import static 

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('register/', views.register_pelanggan, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/<int:mobil_id>/', views.booking_view, name='booking'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('bayar/<int:reservasi_id>/', views.bayar_view, name='bayar'),
    # Include kendaraan_ext app routes (CRUD for kendaraan)
    path('kendaraan/', include('kendaraan_ext.urls')),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)