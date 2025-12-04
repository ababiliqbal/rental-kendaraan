from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import (
    Report, RevenueReport, BookingReport, VehicleReport, 
    UserReport, MaintenanceReport
)
from kendaraan_ext.models import Kendaraan
from manajemen_pengguna.models import Reservasi
from django.contrib.auth.models import User


@staff_member_required
def report_dashboard(request):
    """Dashboard untuk laporan sistem"""
    context = {
        'total_reports': Report.objects.count(),
        'recent_reports': Report.objects.filter(created_by=request.user)[:5],
    }
    return render(request, 'reporting_system/dashboard.html', context)


@staff_member_required
def revenue_report(request):
    """View untuk laporan pendapatan"""
    # Ambil tanggal dari request atau gunakan bulan saat ini
    from django.utils.timezone import now
    today = now().date()
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = today.replace(day=1)
    
    if end_date:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # Query data untuk laporan
    reservasi = Reservasi.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    total_revenue = reservasi.filter(
        status='Selesai'
    ).aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
    
    stats = {
        'total_revenue': total_revenue,
        'total_bookings': reservasi.count(),
        'completed': reservasi.filter(status='Selesai').count(),
        'cancelled': reservasi.filter(status='Batal').count(),
        'pending': reservasi.filter(status='Dipesan').count() + reservasi.filter(status='Aktif').count(),
    }
    
    completed_count = reservasi.filter(status='Selesai').count()
    if completed_count > 0:
        stats['average_booking_value'] = total_revenue / completed_count
    else:
        stats['average_booking_value'] = 0
    
    context = {
        'stats': stats,
        'start_date': start_date,
        'end_date': end_date,
        'reservasi': reservasi,
    }
    return render(request, 'reporting_system/revenue_report.html', context)


@staff_member_required
def booking_report(request):
    """View untuk laporan pemesanan"""
    from django.utils.timezone import now
    today = now().date()
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = today - timedelta(days=30)
    
    if end_date:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today
    
    reservasi = Reservasi.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Kendaraan paling sering dipesankan
    most_booked = reservasi.values('kendaraan').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_booked_vehicle = None
    if most_booked:
        most_booked_vehicle = Kendaraan.objects.get(id=most_booked['kendaraan'])
    
    # User paling aktif
    most_active = reservasi.values('pelanggan').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_active_user = None
    if most_active:
        most_active_user = User.objects.get(id=most_active['pelanggan'])
    
    stats = {
        'total_bookings': reservasi.count(),
        'completed': reservasi.filter(status='Selesai').count(),
        'cancelled': reservasi.filter(status='Batal').count(),
        'pending': reservasi.filter(status='Dipesan').count() + reservasi.filter(status='Aktif').count(),
        'most_booked_vehicle': most_booked_vehicle,
        'most_active_user': most_active_user,
    }
    
    context = {
        'stats': stats,
        'start_date': start_date,
        'end_date': end_date,
        'reservasi': reservasi,
    }
    return render(request, 'reporting_system/booking_report.html', context)


@staff_member_required
def vehicle_report(request):
    """View untuk laporan kendaraan"""
    all_vehicles = Kendaraan.objects.all()
    
    stats = {
        'total_vehicles': all_vehicles.count(),
        'available_vehicles': all_vehicles.filter(status='Tersedia').count(),
        'rented_vehicles': all_vehicles.filter(status='Dirental').count(),
        'maintenance_vehicles': all_vehicles.filter(status='Perawatan').count(),
    }
    
    context = {
        'stats': stats,
        'vehicles': all_vehicles,
    }
    return render(request, 'reporting_system/vehicle_report.html', context)


@staff_member_required
def user_report(request):
    """View untuk laporan pengguna"""
    from django.utils.timezone import now
    today = now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    all_users = User.objects.filter(is_staff=False)
    new_users = all_users.filter(date_joined__date__gte=thirty_days_ago)
    
    total_bookings = Reservasi.objects.count()
    
    stats = {
        'total_users': all_users.count(),
        'active_users': all_users.filter(
            reservasi_saya__status='Selesai'
        ).distinct().count(),
        'new_users': new_users.count(),
        'total_bookings_by_users': total_bookings,
    }
    
    if all_users.count() > 0:
        stats['average_bookings_per_user'] = total_bookings / all_users.count()
    else:
        stats['average_bookings_per_user'] = 0
    
    context = {
        'stats': stats,
        'users': all_users,
    }
    return render(request, 'reporting_system/user_report.html', context)


@staff_member_required
def report_list(request):
    """View untuk menampilkan daftar laporan"""
    reports = Report.objects.filter(created_by=request.user).order_by('-created_date')
    
    context = {
        'reports': reports,
    }
    return render(request, 'reporting_system/report_list.html', context)


@staff_member_required
def report_detail(request, pk):
    """View untuk menampilkan detail laporan"""
    report = get_object_or_404(Report, pk=pk, created_by=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'reporting_system/report_detail.html', context)


@staff_member_required
@permission_required('reporting_system.delete_report', raise_exception=True)
def report_delete(request, pk):
    """View untuk menghapus laporan"""
    report = get_object_or_404(Report, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        report.delete()
        return redirect('reporting_system:report_list')
    
    context = {
        'report': report,
    }
    return render(request, 'reporting_system/report_confirm_delete.html', context)
