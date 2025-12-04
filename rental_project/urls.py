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
    path('booking/<int:mobil_id>/', views.booking_view, name='booking'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('bayar/<int:reservasi_id>/', views.bayar_view, name='bayar'),
    path('reports/', include('reporting_system.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)