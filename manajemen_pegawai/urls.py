from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_pegawai, name='dashboard_pegawai'),
    
    # URL untuk Aksi (Action)
    path('verifikasi/<int:tagihan_id>/<str:aksi>/', views.verifikasi_pembayaran, name='verifikasi_pembayaran'),
    path('update-status/<int:reservasi_id>/<str:status_baru>/', views.update_status_pesanan, name='update_status_pesanan'),
    path('pengembalian/<int:reservasi_id>/', views.proses_pengembalian, name='proses_pengembalian'),
    
    path('armada/', views.daftar_armada, name='daftar_armada'),
    path('armada/tambah-mobil/', views.tambah_mobil, name='tambah_mobil'),
    path('armada/tambah-motor/', views.tambah_motor, name='tambah_motor'),
    path('armada/edit/<int:pk>/', views.edit_armada, name='edit_armada'), # <--- Tambahkan ini
    path('armada/hapus/<int:pk>/', views.hapus_kendaraan, name='hapus_kendaraan'),
]