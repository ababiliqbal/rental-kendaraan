from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Sum, Case, When, IntegerField
from django.utils import timezone

from manajemen_pengguna.models import Reservasi, Pembayaran, Tagihan

def cek_pegawai(user):
    return user.is_authenticated and (user.is_superuser or user.profil.is_pegawai)

@user_passes_test(cek_pegawai, login_url='home')
def dashboard_reporting(request):
    # ==========================================
    # 1. KARTU METRIK UTAMA
    # ==========================================
    total_pendapatan = Pembayaran.objects.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    total_transaksi = Tagihan.objects.filter(status='Lunas').count()

    # ==========================================
    # 2. GRAFIK PENDAPATAN BULANAN (Logic Python)
    # ==========================================
    pembayaran_list = Pembayaran.objects.all() 
    
    data_bulanan = [0] * 12 
    for p in pembayaran_list:
        idx = p.tanggal.month - 1
        data_bulanan[idx] += int(p.jumlah)

    # ==========================================
    # 3. GRAFIK KENDARAAN TERLARIS
    # ==========================================
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

    # ==========================================
    # 4. TABEL TRANSAKSI TERBARU
    # ==========================================
    transaksi_terbaru = Tagihan.objects.filter(status='Lunas').select_related('reservasi').order_by('-id')[:10]

    # ==========================================
    # 5. LAPORAN BAGI HASIL MITRA (BARU)
    # ==========================================
    # Logic: Ambil tagihan lunas yang mobilnya punya mitra, lalu hitung jatahnya.
    laporan_mitra = Tagihan.objects.filter(
        status='Lunas', 
        reservasi__kendaraan__mitra__isnull=False
    ).values(
        'reservasi__kendaraan__mitra__nama', # Group by Nama Mitra
        'reservasi__kendaraan__plat_nomor'   # Group by Mobil
    ).annotate(
        total_omset=Sum('total_akhir'),
        # Rumus: Total Tagihan * Persentase Mitra / 100
        jatah_mitra=Sum(
            F('total_akhir') * F('reservasi__kendaraan__persentase_mitra') / 100,
            output_field=IntegerField()
        )
    ).order_by('reservasi__kendaraan__mitra__nama')

    context = {
        'total_pendapatan': total_pendapatan,
        'total_transaksi': total_transaksi,
        
        # Grafik
        'chart_income_data': data_bulanan, 
        'chart_mobil_labels': label_mobil,
        'chart_mobil_data': data_sewa,
        
        # Tabel
        'transaksi_terbaru': transaksi_terbaru,
        'laporan_mitra': laporan_mitra, # Data mitra dikirim ke sini
    }
    return render(request, 'manajemen_reporting/laporan_dashboard.html', context)