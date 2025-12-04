from django.db import models
from django.contrib.auth.models import User
from kendaraan_ext.models import Kendaraan
from manajemen_pengguna.models import Reservasi


class Report(models.Model):
    """Model untuk menyimpan laporan sistem"""
    REPORT_TYPE_CHOICES = [
        ('revenue', 'Revenue Report'),
        ('booking', 'Booking Report'),
        ('kendaraan', 'Vehicle Report'),
        ('user', 'User Report'),
        ('maintenance', 'Maintenance Report'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"


class RevenueReport(models.Model):
    """Model untuk laporan pendapatan"""
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='revenue_report')
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bookings = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    total_cancelled = models.IntegerField(default=0)
    average_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Revenue Report'
        verbose_name_plural = 'Revenue Reports'
    
    def __str__(self):
        return f"Revenue Report - {self.report.title}"


class BookingReport(models.Model):
    """Model untuk laporan pemesanan"""
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='booking_report')
    total_bookings = models.IntegerField(default=0)
    completed_bookings = models.IntegerField(default=0)
    cancelled_bookings = models.IntegerField(default=0)
    pending_bookings = models.IntegerField(default=0)
    most_booked_vehicle = models.ForeignKey(Kendaraan, on_delete=models.SET_NULL, null=True, blank=True)
    most_active_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_reports')
    
    class Meta:
        verbose_name = 'Booking Report'
        verbose_name_plural = 'Booking Reports'
    
    def __str__(self):
        return f"Booking Report - {self.report.title}"


class VehicleReport(models.Model):
    """Model untuk laporan kendaraan"""
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='vehicle_report')
    total_vehicles = models.IntegerField(default=0)
    available_vehicles = models.IntegerField(default=0)
    rented_vehicles = models.IntegerField(default=0)
    maintenance_vehicles = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Vehicle Report'
        verbose_name_plural = 'Vehicle Reports'
    
    def __str__(self):
        return f"Vehicle Report - {self.report.title}"


class UserReport(models.Model):
    """Model untuk laporan pengguna"""
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='user_report')
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    total_bookings_by_users = models.IntegerField(default=0)
    average_bookings_per_user = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'User Report'
        verbose_name_plural = 'User Reports'
    
    def __str__(self):
        return f"User Report - {self.report.title}"


class MaintenanceReport(models.Model):
    """Model untuk laporan pemeliharaan kendaraan"""
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='maintenance_report')
    total_maintenance = models.IntegerField(default=0)
    completed_maintenance = models.IntegerField(default=0)
    pending_maintenance = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Maintenance Report'
        verbose_name_plural = 'Maintenance Reports'
    
    def __str__(self):
        return f"Maintenance Report - {self.report.title}"
