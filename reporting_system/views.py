from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from kendaraan_ext.models import Kendaraan
from manajemen_pengguna.models import Reservasi

from .forms import CreateReportForm, ReportFilterForm
from .models import (
    Report,
    RevenueReport,
    BookingReport,
    VehicleReport,
    UserReport,
    MaintenanceReport,
)


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
def maintenance_report(request):
    """View untuk laporan perawatan kendaraan"""
    perawatan = Kendaraan.objects.filter(status='Perawatan')
    stats = {
        'total_vehicles': Kendaraan.objects.count(),
        'maintenance_vehicles': perawatan.count(),
    }
    context = {
        'stats': stats,
        'vehicles': perawatan,
    }
    return render(request, 'reporting_system/maintenance_report.html', context)


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
    filter_form = ReportFilterForm(request.GET or None)
    reports = Report.objects.all().order_by('-created_date')

    if filter_form.is_valid():
        report_type = filter_form.cleaned_data.get('report_type')
        status = filter_form.cleaned_data.get('status')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')

        if report_type:
            reports = reports.filter(report_type=report_type)
        if status:
            reports = reports.filter(status=status)
        if start_date:
            reports = reports.filter(created_date__date__gte=start_date)
        if end_date:
            reports = reports.filter(created_date__date__lte=end_date)

    context = {
        'reports': reports,
        'filter_form': filter_form,
    }
    return render(request, 'reporting_system/report_list.html', context)


@staff_member_required
def report_detail(request, pk):
    """View untuk menampilkan detail laporan"""
    report = get_object_or_404(Report, pk=pk)

    context = {
        'report': report,
    }
    return render(request, 'reporting_system/report_detail.html', context)


@staff_member_required
@permission_required('reporting_system.delete_report', raise_exception=True)
def report_delete(request, pk):
    """View untuk menghapus laporan"""
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        report.delete()
        return redirect('reporting_system:report_list')
    
    context = {
        'report': report,
    }
    return render(request, 'reporting_system/report_confirm_delete.html', context)


@staff_member_required
def export_reports_csv(request):
    """Ekspor seluruh laporan ke CSV sederhana"""
    reports = Report.objects.all().order_by('-created_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    response.write("id,title,report_type,status,start_date,end_date,created_date\n")
    for r in reports:
        row = [
            r.id,
            f'"{r.title.replace('"', '""')}"',
            r.report_type,
            r.status,
            r.start_date or '',
            r.end_date or '',
            r.created_date,
        ]
        response.write(",".join(map(str, row)) + "\n")
    return response


@staff_member_required
@permission_required('reporting_system.add_report', raise_exception=True)
@require_http_methods(["GET", "POST"])
def report_create(request):
    """Form untuk membuat laporan baru"""
    if request.method == 'POST':
        form = CreateReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            return redirect('reporting_system:report_detail', pk=report.pk)
    else:
        form = CreateReportForm()

    context = {
        'form': form,
        'mode': 'create',
    }
    return render(request, 'reporting_system/report_form.html', context)


@staff_member_required
@permission_required('reporting_system.change_report', raise_exception=True)
@require_http_methods(["GET", "POST"])
def report_update(request, pk):
    """Form untuk memperbarui laporan"""
    report = get_object_or_404(Report, pk=pk)

    if request.method == 'POST':
        form = CreateReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            updated_report = form.save(commit=False)
            if not updated_report.created_by:
                updated_report.created_by = request.user
            updated_report.save()
            return redirect('reporting_system:report_detail', pk=updated_report.pk)
    else:
        form = CreateReportForm(instance=report)

    context = {
        'form': form,
        'mode': 'update',
        'report': report,
    }
    return render(request, 'reporting_system/report_form.html', context)
