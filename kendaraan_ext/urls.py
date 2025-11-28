from django.urls import path
from . import views

urlpatterns = [
    # URL ROOT BARU: Jika mengakses /, tampilkan MobilListView
    path('', views.MobilListView.as_view(), name='home'), 
    
    # URL List yang sudah ada
    path('mobil/', views.MobilListView.as_view(), name='mobil_list'),
    path('motor/', views.MotorListView.as_view(), name='motor_list'),
    path('garasi/', views.GarasiListView.as_view(), name='garasi_list'),
    path('kendaraanext/', views.KendaraanExtListView.as_view(), name='kendaraanext_list'),
]
