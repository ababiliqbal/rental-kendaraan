"""
Utility functions untuk reporting system
"""
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Report, RevenueReport, BookingReport, VehicleReport, UserReport, MaintenanceReport
from kendaraan_ext.models import Kendaraan
from manajemen_pengguna.models import Reservasi
from django.contrib.auth.models import User


def generate_revenue_report(title, description, start_date, end_date, created_by):
    """Generate laporan pendapatan"""
    report = Report.objects.create(
        report_type='revenue',
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=created_by,
        status='published'
    )
    
    reservasi = Reservasi.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='Selesai'
    )
    
    total_revenue = reservasi.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
    
    revenue_report = RevenueReport.objects.create(
        report=report,
        total_revenue=total_revenue,
        total_bookings=Reservasi.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count(),
        total_completed=reservasi.count(),
        total_cancelled=Reservasi.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='Batal'
        ).count(),
    )
    
    if reservasi.count() > 0:
        revenue_report.average_booking_value = total_revenue / reservasi.count()
        revenue_report.save()
    
    return report, revenue_report


def generate_booking_report(title, description, start_date, end_date, created_by):
    """Generate laporan pemesanan"""
    report = Report.objects.create(
        report_type='booking',
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=created_by,
        status='published'
    )
    
    reservasi = Reservasi.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    most_booked = reservasi.values('kendaraan').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_booked_vehicle = None
    if most_booked:
        most_booked_vehicle = Kendaraan.objects.get(id=most_booked['kendaraan'])
    
    most_active = reservasi.values('pelanggan').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_active_user = None
    if most_active:
        most_active_user = User.objects.get(id=most_active['pelanggan'])
    
    booking_report = BookingReport.objects.create(
        report=report,
        total_bookings=reservasi.count(),
        completed_bookings=reservasi.filter(status='Selesai').count(),
        cancelled_bookings=reservasi.filter(status='Batal').count(),
        pending_bookings=reservasi.filter(status__in=['Dipesan', 'Aktif']).count(),
        most_booked_vehicle=most_booked_vehicle,
        most_active_user=most_active_user
    )
    
    return report, booking_report


def generate_vehicle_report(title, description, created_by):
    """Generate laporan kendaraan"""
    report = Report.objects.create(
        report_type='kendaraan',
        title=title,
        description=description,
        created_by=created_by,
        status='published'
    )
    
    all_vehicles = Kendaraan.objects.all()
    
    vehicle_report = VehicleReport.objects.create(
        report=report,
        total_vehicles=all_vehicles.count(),
        available_vehicles=all_vehicles.filter(status='Tersedia').count(),
        rented_vehicles=all_vehicles.filter(status='Dirental').count(),
        maintenance_vehicles=all_vehicles.filter(status='Perawatan').count(),
    )
    
    return report, vehicle_report


def generate_user_report(title, description, created_by):
    """Generate laporan pengguna"""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    report = Report.objects.create(
        report_type='user',
        title=title,
        description=description,
        created_by=created_by,
        status='published'
    )
    
    all_users = User.objects.filter(is_staff=False)
    new_users = all_users.filter(date_joined__date__gte=thirty_days_ago)
    total_bookings = Reservasi.objects.count()
    
    user_report = UserReport.objects.create(
        report=report,
        total_users=all_users.count(),
        active_users=all_users.filter(reservasi_saya__status='Selesai').distinct().count(),
        new_users=new_users.count(),
        total_bookings_by_users=total_bookings,
    )
    
    if all_users.count() > 0:
        user_report.average_bookings_per_user = total_bookings / all_users.count()
        user_report.save()
    
    return report, user_report


def get_revenue_summary(start_date, end_date):
    """Get ringkasan revenue dalam periode tertentu"""
    reservasi = Reservasi.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    completed = reservasi.filter(status='Selesai')
    total_revenue = completed.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
    
    return {
        'total_revenue': total_revenue,
        'total_bookings': reservasi.count(),
        'completed_bookings': completed.count(),
        'cancelled_bookings': reservasi.filter(status='Batal').count(),
        'pending_bookings': reservasi.filter(status__in=['Dipesan', 'Aktif']).count(),
    }


def get_top_vehicles(limit=5):
    """Get top kendaraan yang paling sering disewa"""
    return Reservasi.objects.values('kendaraan', 'kendaraan__merk', 'kendaraan__model').annotate(
        count=Count('id')
    ).order_by('-count')[:limit]


def get_top_users(limit=5):
    """Get top pengguna yang paling sering booking"""
    return Reservasi.objects.values('pelanggan', 'pelanggan__username').annotate(
        count=Count('id')
    ).order_by('-count')[:limit]
