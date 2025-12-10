from django.urls import path
from . import views

app_name = 'reporting_system'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('booking/', views.booking_report, name='booking_report'),
    path('vehicle/', views.vehicle_report, name='vehicle_report'),
    path('user/', views.user_report, name='user_report'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/edit/', views.report_update, name='report_update'),
    path('reports/<int:pk>/delete/', views.report_delete, name='report_delete'),
]
