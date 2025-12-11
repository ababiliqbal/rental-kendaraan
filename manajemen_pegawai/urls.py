from django.urls import path
from . import views

from .views import (
    PegawaiListView, PegawaiDetailView, PegawaiCreateView, 
    PegawaiUpdateView, PegawaiDeleteView,
    ShiftListView, ShiftCreateView, ShiftUpdateView, ShiftDetailView, ShiftDeleteView,
    GajiPegawaiListView, GajiPegawaiCreateView, GajiPegawaiUpdateView, GajiPegawaiDetailView,
    JadwalKerjaListView, JadwalKerjaCreateView, JadwalKerjaDetailView, 
    JadwalKerjaUpdateView, JadwalKerjaDeleteView,
)

urlpatterns = [
    path('', views.dashboard_pegawai, name='dashboard_pegawai'),
    
    # URL untuk Aksi (Action)
    path('verifikasi/<int:tagihan_id>/<str:aksi>/', views.verifikasi_pembayaran, name='verifikasi_pembayaran'),
    path('update-status/<int:reservasi_id>/<str:status_baru>/', views.update_status_pesanan, name='update_status_pesanan'),
    path('pengembalian/<int:reservasi_id>/', views.proses_pengembalian, name='proses_pengembalian'),
    
    path('armada/', views.daftar_armada, name='daftar_armada'),
    path('armada/tambah-mobil/', views.tambah_mobil, name='tambah_mobil'),
    path('armada/tambah-motor/', views.tambah_motor, name='tambah_motor'),
    path('armada/edit/<int:pk>/', views.edit_armada, name='edit_armada'), 
    path('armada/hapus/<int:pk>/', views.hapus_kendaraan, name='hapus_kendaraan'),
    
    path('mitra/', views.daftar_mitra, name='daftar_mitra'),
    path('mitra/tambah/', views.tambah_mitra, name='tambah_mitra'),
    path('mitra/edit/<int:pk>/', views.edit_mitra, name='edit_mitra'),
    path('mitra/hapus/<int:pk>/', views.hapus_mitra, name='hapus_mitra'),
    
    # Pegawai
    path('data-pegawai/', PegawaiListView.as_view(), name='pegawai_list'),
    path('data-pegawai/tambah/', PegawaiCreateView.as_view(), name='pegawai_create'),
    path('data-pegawai/<int:pk>/', PegawaiDetailView.as_view(), name='pegawai_detail'),
    path('data-pegawai/<int:pk>/edit/', PegawaiUpdateView.as_view(), name='pegawai_update'),
    path('data-pegawai/<int:pk>/hapus/', PegawaiDeleteView.as_view(), name='pegawai_delete'),
    
    # Shift
    path('shift/', ShiftListView.as_view(), name='shift_list'),
    path('shift/tambah/', ShiftCreateView.as_view(), name='shift_create'),
    path('shift/<int:pk>/', ShiftDetailView.as_view(), name='shift_detail'),
    path('shift/<int:pk>/edit/', ShiftUpdateView.as_view(), name='shift_update'),
    path('shift/<int:pk>/hapus/', ShiftDeleteView.as_view(), name='shift_delete'),
    
    # Gaji
    path('gaji/', GajiPegawaiListView.as_view(), name='gaji_list'),
    path('gaji/buat/', GajiPegawaiCreateView.as_view(), name='gaji_create'),
    path('gaji/<int:pk>/', GajiPegawaiDetailView.as_view(), name='gaji_detail'), 
    path('gaji/<int:pk>/edit/', GajiPegawaiUpdateView.as_view(), name='gaji_update'),
    
    # Jadwal
    path('jadwal/', JadwalKerjaListView.as_view(), name='jadwal_list'),
    path('jadwal/tambah/', JadwalKerjaCreateView.as_view(), name='jadwal_create'),
    path('jadwal/<int:pk>/', JadwalKerjaDetailView.as_view(), name='jadwal_detail'),
    path('jadwal/<int:pk>/edit/', JadwalKerjaUpdateView.as_view(), name='jadwal_update'),
    path('jadwal/<int:pk>/hapus/', JadwalKerjaDeleteView.as_view(), name='jadwal_delete'),
]