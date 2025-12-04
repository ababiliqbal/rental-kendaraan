from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction # WAJIB IMPORT INI

# Import Model dari App Tetangga
from manajemen_pengguna.models import Reservasi, Tagihan, Denda
from kendaraan_ext.models import Kendaraan
from .forms import FormPengembalian, KendaraanForm, MobilForm, MotorForm
import datetime

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

# ... (dashboard_pegawai & verifikasi_pembayaran biarkan saja) ...

@user_passes_test(cek_pegawai, login_url='home')
def proses_pengembalian(request, reservasi_id):
    reservasi = get_object_or_404(Reservasi, id=reservasi_id)
    tagihan = reservasi.tagihan # Ambil tagihan terkait
    
    # Hitung Keterlambatan Otomatis
    today = timezone.now().date()
    tgl_selesai = reservasi.tgl_selesai
    
    telat_hari = 0
    denda_telat = 0
    
    if today > tgl_selesai:
        telat_hari = (today - tgl_selesai).days
        # Rumus: Denda Telat = Hari Telat x Harga Sewa Per Hari
        denda_telat = telat_hari * reservasi.kendaraan.harga_sewa_per_hari

    if request.method == 'POST':
        form = FormPengembalian(request.POST)
        if form.is_valid():
            # 1. Simpan Denda Keterlambatan (Kalau ada)
            if denda_telat > 0:
                Denda.objects.create(
                    tagihan=tagihan,
                    jenis="Keterlambatan",
                    jumlah=denda_telat,
                    keterangan=f"Telat {telat_hari} hari (x Rp {reservasi.kendaraan.harga_sewa_per_hari})"
                )

            # 2. Simpan Denda Kerusakan (Dari Form)
            biaya_rusak = form.cleaned_data['denda_kerusakan']
            ket_rusak = form.cleaned_data['keterangan_kerusakan']
            
            if biaya_rusak > 0:
                Denda.objects.create(
                    tagihan=tagihan,
                    jenis="Kerusakan Fisik",
                    jumlah=biaya_rusak,
                    keterangan=ket_rusak
                )
            
            # 3. Update Total Tagihan
            total_denda = denda_telat + biaya_rusak
            if total_denda > 0:
                tagihan.total_denda = total_denda
                tagihan.total_akhir += total_denda
                tagihan.status = 'Belum Lunas' # Ubah jadi Belum Lunas biar user bayar dendanya
                tagihan.save()
                messages.warning(request, f"Pengembalian tercatat dengan total denda Rp {total_denda:,}. Tagihan diperbarui.")
            else:
                messages.success(request, "Mobil dikembalikan tepat waktu & tanpa kerusakan. Sewa Selesai.")

            # 4. Update Status Reservasi & Mobil
            reservasi.status = 'Selesai'
            reservasi.tgl_pengembalian_aktual = today
            reservasi.save()
            
            reservasi.kendaraan.status = 'Tersedia'
            reservasi.kendaraan.save()
            
            return redirect('dashboard_pegawai')

    else:
        form = FormPengembalian()

    context = {
        'reservasi': reservasi,
        'form': form,
        'telat_hari': telat_hari,
        'denda_telat': denda_telat,
    }
    return render(request, 'manajemen_pegawai/form_pengembalian.html', context)

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

# ==========================================
# MANAJEMEN ARMADA (CRUD)
# ==========================================

@user_passes_test(cek_pegawai, login_url='home')
def daftar_armada(request):
    # Ambil semua kendaraan, urutkan dari yang terbaru
    armada = Kendaraan.objects.all().order_by('-id')
    return render(request, 'manajemen_pegawai/daftar_armada.html', {'armada': armada})

@user_passes_test(cek_pegawai, login_url='home')
def tambah_mobil(request):
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES)
        m_form = MobilForm(request.POST)
        
        if k_form.is_valid() and m_form.is_valid():
            try:
                with transaction.atomic(): # Transaksi Database Aman
                    # 1. Simpan Kendaraan (Induk)
                    kendaraan = k_form.save()
                    
                    # 2. Simpan Mobil (Anak) & Hubungkan
                    mobil = m_form.save(commit=False)
                    mobil.kendaraan = kendaraan # Link OneToOne
                    mobil.save()
                    
                messages.success(request, f"Mobil {kendaraan.merk} {kendaraan.model} berhasil ditambahkan!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {e}")
    else:
        k_form = KendaraanForm()
        m_form = MobilForm()

    context = {
        'k_form': k_form, 
        'm_form': m_form, 
        'title': 'Tambah Mobil Baru',
        'icon': 'fa-car'
    }
    return render(request, 'manajemen_pegawai/form_armada.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def tambah_motor(request):
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES)
        m_form = MotorForm(request.POST)
        
        if k_form.is_valid() and m_form.is_valid():
            try:
                with transaction.atomic():
                    kendaraan = k_form.save()
                    motor = m_form.save(commit=False)
                    motor.kendaraan = kendaraan
                    motor.save()
                    
                messages.success(request, f"Motor {kendaraan.merk} {kendaraan.model} berhasil ditambahkan!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Gagal menyimpan: {e}")
    else:
        k_form = KendaraanForm()
        m_form = MotorForm()

    context = {
        'k_form': k_form, 
        'm_form': m_form, 
        'title': 'Tambah Motor Baru',
        'icon': 'fa-motorcycle'
    }
    # Kita pakai template yang sama (Reusable Template)
    return render(request, 'manajemen_pegawai/form_armada.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def hapus_kendaraan(request, pk):
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    if request.method == 'POST':
        kendaraan.delete()
        messages.success(request, "Data kendaraan berhasil dihapus.")
        return redirect('daftar_armada')

# manajemen_pegawai/views.py

@user_passes_test(cek_pegawai, login_url='home')
def edit_armada(request, pk):
    # 1. Ambil data kendaraan induk
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    
    # 2. Deteksi Jenis & Siapkan Variable
    child_instance = None
    ChildForm = None
    jenis_str = ""
    icon = ""

    if hasattr(kendaraan, 'detail_mobil'):
        child_instance = kendaraan.detail_mobil
        ChildForm = MobilForm
        jenis_str = "Mobil"
        icon = "fa-car"
    elif hasattr(kendaraan, 'detail_motor'):
        child_instance = kendaraan.detail_motor
        ChildForm = MotorForm
        jenis_str = "Motor"
        icon = "fa-motorcycle"
    
    if ChildForm is None:
        messages.error(request, f"Data kendaraan '{kendaraan.plat_nomor}' tidak valid atau tidak lengkap (Hanya data induk). Silakan hapus dan buat ulang.")
        return redirect('daftar_armada')
    
    # 3. Proses Form
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES, instance=kendaraan)
        # Load form anak dengan instance yang sesuai
        c_form = ChildForm(request.POST, instance=child_instance)
        
        if k_form.is_valid() and c_form.is_valid():
            try:
                with transaction.atomic():
                    k_form.save()
                    c_form.save()
                messages.success(request, f"Data {jenis_str} {kendaraan.merk} berhasil diperbarui!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        # GET: Isi form dengan data yang sudah ada
        k_form = KendaraanForm(instance=kendaraan)
        c_form = ChildForm(instance=child_instance)

    context = {
        'k_form': k_form,
        'm_form': c_form, # Kita pakai nama variabel yang sama dgn 'tambah' biar template reusable
        'title': f'Edit Data {jenis_str}',
        'icon': icon,
        'is_edit': True # Flag untuk membedakan tampilan tombol
    }
    
    # Kita gunakan template yang sama dengan Tambah Armada
    return render(request, 'manajemen_pegawai/form_armada.html', context)