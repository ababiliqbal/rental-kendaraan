from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_reporting, name='dashboard_reporting'),
]