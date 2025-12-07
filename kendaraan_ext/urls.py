# kendaraan/urls.py (Kode FINAL)

from django.urls import path
from . import views

# --- PERBAIKAN 1: Tambahkan Application Namespace ---
app_name = 'kendaraan' 

urlpatterns = [
    # ==============================
    # URLS KENDARAAN (CRUD)
    # ==============================
    
    # List Kendaraan: http://127.0.0.1:8000/
    path('', views.DaftarKendaraanView.as_view(), name='daftar_kendaraan'), # Menggunakan nama views yang kita sepakati
    
    # Tambah Kendaraan: http://127.0.0.1:8000/tambah/
    # --- PERBAIKAN 2: Hapus 'kendaraan/' dari path ---
    path('tambah/', views.tambah_kendaraan, name='tambah_kendaraan'), 
    
    # Detail Kendaraan: http://127.0.0.1:8000/1/
    # --- PERBAIKAN 2: Hapus 'kendaraan/' dari path ---
    path('<int:pk>/', views.DetailKendaraanView.as_view(), name='detail_kendaraan'), 
    
    # Edit Kendaraan: http://127.0.0.1:8000/1/edit/
    # --- PERBAIKAN 2: Hapus 'kendaraan/' dari path ---
    path('<int:pk>/edit/', views.edit_kendaraan, name='edit_kendaraan'), 
    
    # Hapus Kendaraan: http://127.0.0.1:8000/1/hapus/
    # --- PERBAIKAN 2: Hapus 'kendaraan/' dari path ---
    path('<int:pk>/hapus/', views.HapusKendaraanView.as_view(), name='hapus_kendaraan'),
    
    # ==============================
    # URLS GARASI (CRUD)
    # Garasi sudah memiliki prefiks 'garasi/', jadi ini sudah benar.
    # ==============================
    path('garasi/', views.DaftarGarasiView.as_view(), name='garasi_list'),
    path('garasi/tambah/', views.TambahGarasiView.as_view(), name='garasi_create'),
    path('garasi/<int:pk>/', views.DetailGarasiView.as_view(), name='garasi_detail'),
    path('garasi/<int:pk>/edit/', views.EditGarasiView.as_view(), name='garasi_update'),
    path('garasi/<int:pk>/hapus/', views.HapusGarasiView.as_view(), name='garasi_delete'),
    
    # ===== Mobil Routes =====
    path('mobil/', views.DaftarMobilView.as_view(), name='mobil_list'),
    path('mobil/tambah/', views.TambahMobilView.as_view(), name='mobil_create'),
    path('mobil/<int:pk>/', views.DetailMobilView.as_view(), name='mobil_detail'),
    path('mobil/<int:pk>/edit/', views.EditMobilView.as_view(), name='mobil_update'),
    path('mobil/<int:pk>/hapus/', views.HapusMobilView.as_view(), name='mobil_delete'),

    # ===== Motor Routes =====
    path('motor/', views.DaftarMotorView.as_view(), name='motor_list'),
    path('motor/tambah/', views.TambahMotorView.as_view(), name='motor_create'),
    path('motor/<int:pk>/', views.DetailMotorView.as_view(), name='motor_detail'),
    path('motor/<int:pk>/edit/', views.EditMotorView.as_view(), name='motor_update'),
    path('motor/<int:pk>/hapus/', views.HapusMotorView.as_view(), name='motor_delete'),
]