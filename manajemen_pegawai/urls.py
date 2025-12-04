from django.urls import path
from .views import (
    PegawaiListView, PegawaiDetailView, PegawaiCreateView, 
    PegawaiUpdateView, PegawaiDeleteView,
    ShiftListView, ShiftCreateView, ShiftUpdateView,
    GajiPegawaiListView, GajiPegawaiCreateView, GajiPegawaiUpdateView,
    JadwalKerjaListView, JadwalKerjaCreateView,
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
    path('shift/create/', ShiftCreateView.as_view(), name='shift_create'),
    path('shift/update/<int:pk>/', ShiftUpdateView.as_view(), name='shift_update'),
    
    # Gaji URLs
    path('gaji/', GajiPegawaiListView.as_view(), name='gaji_list'),
    path('gaji/create/', GajiPegawaiCreateView.as_view(), name='gaji_create'),
    path('gaji/update/<int:pk>/', GajiPegawaiUpdateView.as_view(), name='gaji_update'),
    
    # Jadwal Kerja URLs
    path('jadwal/', JadwalKerjaListView.as_view(), name='jadwal_list'),
    path('jadwal/create/', JadwalKerjaCreateView.as_view(), name='jadwal_create'),
]
