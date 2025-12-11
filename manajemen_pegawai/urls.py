from django.urls import path
from .views import (
    PegawaiListView, PegawaiDetailView, PegawaiCreateView, 
    PegawaiUpdateView, PegawaiDeleteView,
    ShiftListView, ShiftCreateView, ShiftUpdateView, ShiftDetailView, ShiftDeleteView,
    GajiPegawaiListView, GajiPegawaiCreateView, GajiPegawaiUpdateView, GajiPegawaiDetailView,
    JadwalKerjaListView, JadwalKerjaCreateView, JadwalKerjaDetailView, 
    JadwalKerjaUpdateView, JadwalKerjaDeleteView,
)

urlpatterns = [
    # Pegawai URLs
    path('', PegawaiListView.as_view(), name='pegawai_list'),
    path('detail/<int:pk>/', PegawaiDetailView.as_view(), name='pegawai_detail'),
    path('create/', PegawaiCreateView.as_view(), name='pegawai_create'),
    path('update/<int:pk>/', PegawaiUpdateView.as_view(), name='pegawai_update'),
    path('delete/<int:pk>/', PegawaiDeleteView.as_view(), name='pegawai_delete'),
    
    # Shift URLs
    path('shift/', ShiftListView.as_view(), name='shift_list'),
    path('shift/tambah/', ShiftCreateView.as_view(), name='shift_create'),
    path('shift/<int:pk>/', ShiftDetailView.as_view(), name='shift_detail'),
    path('shift/<int:pk>/edit/', ShiftUpdateView.as_view(), name='shift_update'),
    path('shift/<int:pk>/hapus/', ShiftDeleteView.as_view(), name='shift_delete'),
    
    # Gaji URLs
    path('gaji/', GajiPegawaiListView.as_view(), name='gaji_list'),
    path('gaji/create/', GajiPegawaiCreateView.as_view(), name='gaji_create'),
    path('gaji/<int:pk>/', GajiPegawaiDetailView.as_view(), name='gaji_detail'), 
    path('gaji/update/<int:pk>/', GajiPegawaiUpdateView.as_view(), name='gaji_update'),
    
    # Jadwal Kerja URLs
    path('jadwal/', JadwalKerjaListView.as_view(), name='jadwal_list'),
    path('jadwal/tambah/', JadwalKerjaCreateView.as_view(), name='jadwal_create'),
    path('jadwal/<int:pk>/', JadwalKerjaDetailView.as_view(), name='jadwal_detail'),
    path('jadwal/<int:pk>/edit/', JadwalKerjaUpdateView.as_view(), name='jadwal_update'),
    path('jadwal/<int:pk>/hapus/', JadwalKerjaDeleteView.as_view(), name='jadwal_delete'),
]
