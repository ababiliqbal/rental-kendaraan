from django.contrib import admin
from .models import (
    Report, RevenueReport, BookingReport, VehicleReport, 
    UserReport, MaintenanceReport
)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'status', 'created_by', 'created_date')
    list_filter = ('report_type', 'status', 'created_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_date', 'modified_date')
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'description', 'status')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_date', 'modified_date', 'file_path')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RevenueReport)
class RevenueReportAdmin(admin.ModelAdmin):
    list_display = ('get_report_title', 'total_revenue', 'total_bookings', 'average_booking_value')
    readonly_fields = ('total_revenue', 'total_bookings', 'average_booking_value')
    
    def get_report_title(self, obj):
        return obj.report.title
    get_report_title.short_description = 'Report'


@admin.register(BookingReport)
class BookingReportAdmin(admin.ModelAdmin):
    list_display = ('get_report_title', 'total_bookings', 'completed_bookings', 'cancelled_bookings')
    readonly_fields = ('total_bookings', 'completed_bookings', 'cancelled_bookings')
    
    def get_report_title(self, obj):
        return obj.report.title
    get_report_title.short_description = 'Report'


@admin.register(VehicleReport)
class VehicleReportAdmin(admin.ModelAdmin):
    list_display = ('get_report_title', 'total_vehicles', 'available_vehicles', 'rented_vehicles')
    readonly_fields = ('total_vehicles', 'available_vehicles', 'rented_vehicles')
    
    def get_report_title(self, obj):
        return obj.report.title
    get_report_title.short_description = 'Report'


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('get_report_title', 'total_users', 'active_users', 'new_users')
    readonly_fields = ('total_users', 'active_users', 'new_users')
    
    def get_report_title(self, obj):
        return obj.report.title
    get_report_title.short_description = 'Report'


@admin.register(MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
    list_display = ('get_report_title', 'total_maintenance', 'completed_maintenance', 'total_cost')
    readonly_fields = ('total_maintenance', 'completed_maintenance', 'total_cost')
    
    def get_report_title(self, obj):
        return obj.report.title
    get_report_title.short_description = 'Report'
