from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_pegawai, name='dashboard_pegawai'),
    
    # URL untuk Aksi (Action)
    path('verifikasi/<int:tagihan_id>/<str:aksi>/', views.verifikasi_pembayaran, name='verifikasi_pembayaran'),
    path('update-status/<int:reservasi_id>/<str:status_baru>/', views.update_status_pesanan, name='update_status_pesanan'),
]