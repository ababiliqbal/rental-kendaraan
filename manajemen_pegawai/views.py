from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone

# Import Model dari App Tetangga
from manajemen_pengguna.models import Reservasi, Tagihan
from kendaraan_ext.models import Kendaraan

# --- DECORATOR KHUSUS ---
# Hanya user dengan flag is_pegawai=True atau Superuser yang boleh masuk
def cek_pegawai(user):
    return user.is_authenticated and (user.is_superuser or user.profil.is_pegawai)

@user_passes_test(cek_pegawai, login_url='home')
def dashboard_pegawai(request):
    # 1. Ambil data Tagihan yang statusnya "Menunggu Verifikasi" (Prioritas Utama)
    tagihan_pending = Tagihan.objects.filter(status='Menunggu Verifikasi').order_by('id')
    
    # 2. Ambil Reservasi yang aktif (Sedang jalan / Perlu diambil)
    reservasi_aktif = Reservasi.objects.filter(status__in=['Dipesan', 'Aktif']).order_by('-tgl_mulai')
    
    context = {
        'tagihan_pending': tagihan_pending,
        'reservasi_aktif': reservasi_aktif,
        'total_pending': tagihan_pending.count(),
        'total_aktif': reservasi_aktif.count()
    }
    return render(request, 'manajemen_pegawai/dashboard.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def verifikasi_pembayaran(request, tagihan_id, aksi):
    tagihan = get_object_or_404(Tagihan, id=tagihan_id)
    
    if aksi == 'terima':
        tagihan.status = 'Lunas'
        tagihan.save()
        messages.success(request, f"Pembayaran Order #{tagihan.reservasi.id} DITERIMA!")
    elif aksi == 'tolak':
        tagihan.status = 'Belum Lunas' # Kembalikan status agar user upload ulang
        tagihan.save()
        messages.warning(request, f"Pembayaran Order #{tagihan.reservasi.id} DITOLAK.")
        
    return redirect('dashboard_pegawai')

@user_passes_test(cek_pegawai, login_url='home')
def update_status_pesanan(request, reservasi_id, status_baru):
    reservasi = get_object_or_404(Reservasi, id=reservasi_id)
    kendaraan = reservasi.kendaraan
    
    if status_baru == 'aktif':
        # Mobil Diambil Pelanggan
        reservasi.status = 'Aktif'
        reservasi.save()
        
        # Update Status Kendaraan jadi "Dirental"
        kendaraan.status = 'Dirental'
        kendaraan.save()
        messages.info(request, "Mobil telah diserahterimakan (Sewa Dimulai).")
        
    elif status_baru == 'selesai':
        # Mobil Dikembalikan
        reservasi.status = 'Selesai'
        reservasi.tgl_pengembalian_aktual = timezone.now().date()
        reservasi.save()
        
        # Update Status Kendaraan jadi "Tersedia" lagi
        kendaraan.status = 'Tersedia'
        kendaraan.save()
        messages.success(request, "Mobil telah dikembalikan (Sewa Selesai).")

    return redirect('dashboard_pegawai')