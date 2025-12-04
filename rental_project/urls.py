from django.contrib import admin
from django.urls import path, include
from manajemen_pengguna import views  # <--- GANTI rental_app JADI manajemen_pengguna
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('', views.home, name='home'), 
    path('admin/', admin.site.urls),
    path('register/', views.register_pelanggan, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/<int:mobil_id>/', views.booking_view, name='booking'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('bayar/<int:reservasi_id>/', views.bayar_view, name='bayar'),
    path('profil/', views.profil_view, name='profil'),
    path('ganti-password/', views.ganti_password_view, name='ganti_password'),
    path('pegawai/', include('manajemen_pegawai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)