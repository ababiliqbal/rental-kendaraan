from django.contrib import admin
from django.urls import path, include
from manajemen_pengguna import views  # <--- GANTI rental_app JADI manajemen_pengguna
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

class AdminLoginView(LoginView):
    template_name = 'admin_login.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prefill_username'] = 'testadmin'
        context['prefill_password'] = 'TestPass123!'
        return context
    def get_success_url(self):
        return '/admin/'

urlpatterns = [
    path('', views.home, name='home'), 
    # path('admin/', admin.site.urls),  # Django admin dinonaktifkan
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('register/', views.register_pelanggan, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/kendaraan/', views.admin_kendaraan_list, name='admin_kendaraan_list'),
    path('admin-dashboard/kendaraan/create/', views.admin_kendaraan_create, name='admin_kendaraan_create'),
    path('admin-dashboard/kendaraan/<int:pk>/edit/', views.admin_kendaraan_update, name='admin_kendaraan_update'),
    path('admin-dashboard/kendaraan/<int:pk>/delete/', views.admin_kendaraan_delete, name='admin_kendaraan_delete'),
    path('admin-dashboard/reservasi/', views.admin_reservasi_list, name='admin_reservasi_list'),
    path('admin-dashboard/reservasi/create/', views.admin_reservasi_create, name='admin_reservasi_create'),
    path('admin-dashboard/reservasi/<int:pk>/edit/', views.admin_reservasi_update, name='admin_reservasi_update'),
    path('admin-dashboard/reservasi/<int:pk>/delete/', views.admin_reservasi_delete, name='admin_reservasi_delete'),
    path('admin-dashboard/tagihan/', views.admin_tagihan_list, name='admin_tagihan_list'),
    path('admin-dashboard/tagihan/create/', views.admin_tagihan_create, name='admin_tagihan_create'),
    path('admin-dashboard/tagihan/<int:pk>/edit/', views.admin_tagihan_update, name='admin_tagihan_update'),
    path('admin-dashboard/tagihan/<int:pk>/delete/', views.admin_tagihan_delete, name='admin_tagihan_delete'),
    path('admin-dashboard/pengguna/', views.admin_pengguna_list, name='admin_pengguna_list'),
    path('admin-dashboard/pengguna/create/', views.admin_pengguna_create, name='admin_pengguna_create'),
    path('admin-dashboard/pengguna/<int:pk>/edit/', views.admin_pengguna_update, name='admin_pengguna_update'),
    path('admin-dashboard/pengguna/<int:pk>/delete/', views.admin_pengguna_delete, name='admin_pengguna_delete'),
    path('booking/<int:mobil_id>/', views.booking_view, name='booking'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('bayar/<int:reservasi_id>/', views.bayar_view, name='bayar'),
    path('reports/', include('reporting_system.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)