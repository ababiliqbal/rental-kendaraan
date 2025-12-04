from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.utils import timezone

from manajemen_pengguna.models import Reservasi, Pembayaran, Tagihan

def cek_pegawai(user):
    return user.is_authenticated and (user.is_superuser or user.profil.is_pegawai)

@user_passes_test(cek_pegawai, login_url='home')
def dashboard_reporting(request):
    # 1. KARTU METRIK
    total_pendapatan = Pembayaran.objects.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    total_transaksi = Tagihan.objects.filter(status='Lunas').count()

    # 2. GRAFIK PENDAPATAN (Logic Python)
    pembayaran_list = Pembayaran.objects.all() # Ambil semua (Logic sederhana untuk MVP)
    
    data_bulanan = [0] * 12 
    for p in pembayaran_list:
        idx = p.tanggal.month - 1
        data_bulanan[idx] += int(p.jumlah)

    # 3. GRAFIK KENDARAAN TERLARIS
    semua_reservasi = Reservasi.objects.all()
    counter_mobil = {}

    for res in semua_reservasi:
        nama_unit = f"{res.kendaraan.merk} {res.kendaraan.model}"
        if nama_unit in counter_mobil:
            counter_mobil[nama_unit] += 1
        else:
            counter_mobil[nama_unit] = 1
    
    top_mobil = sorted(counter_mobil.items(), key=lambda x: x[1], reverse=True)[:5]
    
    label_mobil = [item[0] for item in top_mobil]
    data_sewa = [item[1] for item in top_mobil]

    # 4. TABEL TRANSAKSI
    transaksi_terbaru = Tagihan.objects.filter(status='Lunas').select_related('reservasi').order_by('-id')[:10]

    context = {
        'total_pendapatan': total_pendapatan,
        'total_transaksi': total_transaksi,
        
        # PERBAIKAN DI SINI: Kirim LIST biasa, JANGAN di-dumps!
        'chart_income_data': data_bulanan, 
        'chart_mobil_labels': label_mobil,
        'chart_mobil_data': data_sewa,
        
        'transaksi_terbaru': transaksi_terbaru
    }
    return render(request, 'manajemen_reporting/laporan_dashboard.html', context)