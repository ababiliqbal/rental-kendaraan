from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Import Model
from kendaraan_ext.models import Kendaraan
from .models import Reservasi, Tagihan, Pembayaran, ProfilPengguna
from .forms import (
    RegistrasiPelangganForm,
    ReservasiForm,
    PembayaranForm,
    KendaraanAdminForm,
    ReservasiAdminForm,
    TagihanAdminForm,
    UserAdminCreateForm,
    UserAdminUpdateForm,
)

# ==========================================
# 1. HALAMAN UTAMA (HOME)
# ==========================================
def home(request):
    # Menampilkan mobil yang tersedia
    kendaraan_list = Kendaraan.objects.filter(status='Tersedia')
    context = {
        'kendaraan_list': kendaraan_list
    }
    # Perhatikan nama foldernya: 'manajemen_pengguna/home.html'
    return render(request, 'manajemen_pengguna/home.html', context)

# ==========================================
# 2. AUTENTIKASI (Register, Login, Logout)
# ==========================================
def register_pelanggan(request):
    if request.method == 'POST':
        form = RegistrasiPelangganForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
    else:
        form = RegistrasiPelangganForm()
    return render(request, 'manajemen_pengguna/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang, {username}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Username atau password tidak valid.")
    else:
        form = AuthenticationForm()
    return render(request, 'manajemen_pengguna/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Anda berhasil logout.")
    return redirect('login')

# ==========================================
# 3. TRANSAKSI (Booking & Bayar)
# ==========================================
@login_required(login_url='login')
def booking_view(request, mobil_id):
    mobil = get_object_or_404(Kendaraan, id=mobil_id)
    
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            reservasi = form.save(commit=False)
            reservasi.pelanggan = request.user
            reservasi.kendaraan = mobil
            
            durasi = (reservasi.tgl_selesai - reservasi.tgl_mulai).days
            if durasi <= 0:
                messages.error(request, "Tanggal selesai harus lebih besar dari tanggal mulai!")
                return render(request, 'manajemen_pengguna/booking_form.html', {'form': form, 'mobil': mobil})
                
            reservasi.total_biaya = durasi * mobil.harga_sewa_per_hari
            reservasi.status = 'Dipesan'
            reservasi.save()
            
            Tagihan.objects.create(reservasi=reservasi, total_akhir=reservasi.total_biaya)
            
            messages.success(request, f"Booking berhasil! Total: Rp {reservasi.total_biaya:,}")
            return redirect('riwayat')
    else:
        form = ReservasiForm()

    return render(request, 'manajemen_pengguna/booking_form.html', {'form': form, 'mobil': mobil})

@login_required(login_url='login')
def riwayat_view(request):
    reservasi_list = Reservasi.objects.filter(pelanggan=request.user).order_by('-id')
    return render(request, 'manajemen_pengguna/riwayat.html', {'reservasi_list': reservasi_list})

@login_required(login_url='login')
def bayar_view(request, reservasi_id):
    reservasi = get_object_or_404(Reservasi, id=reservasi_id, pelanggan=request.user)
    
    tagihan, created = Tagihan.objects.get_or_create(
        reservasi=reservasi,
        defaults={'total_akhir': reservasi.total_biaya} 
    )

    if request.method == 'POST':
        form = PembayaranForm(request.POST, request.FILES)
        if form.is_valid():
            pembayaran = form.save(commit=False)
            pembayaran.tagihan = tagihan
            pembayaran.metode = 'Transfer'
            pembayaran.save()
            
            # Update status jadi Menunggu Verifikasi
            tagihan.status = 'Menunggu Verifikasi'
            tagihan.save()
            
            messages.success(request, "Bukti transfer berhasil diupload!")
            return redirect('riwayat')
    else:
        form = PembayaranForm(initial={'jumlah': reservasi.total_biaya})

    return render(request, 'manajemen_pengguna/bayar_form.html', {'form': form, 'reservasi': reservasi})

# ==========================================
# 4. HALAMAN ADMIN (Staff Only)
# ==========================================
@login_required(login_url='login')
def admin_dashboard(request):
    # Hanya staff yang dapat mengakses
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses ke halaman admin.")
        return redirect('home')
    
    # Data untuk admin dashboard
    total_kendaraan = Kendaraan.objects.count()
    kendaraan_tersedia = Kendaraan.objects.filter(status='Tersedia').count()
    kendaraan_dirental = Kendaraan.objects.filter(status='Dirental').count()
    total_reservasi = Reservasi.objects.count()
    
    context = {
        'total_kendaraan': total_kendaraan,
        'kendaraan_tersedia': kendaraan_tersedia,
        'kendaraan_dirental': kendaraan_dirental,
        'total_reservasi': total_reservasi,
    }
    
    return render(request, 'manajemen_pengguna/admin_dashboard.html', context)


# ==========================================
# 5. CRUD KENDARAAN (Admin)
# ==========================================
@login_required(login_url='login')
def admin_kendaraan_list(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    kendaraan_list = Kendaraan.objects.all().order_by('-id')
    return render(request, 'manajemen_pengguna/admin_kendaraan_list.html', {'kendaraan_list': kendaraan_list})


@login_required(login_url='login')
def admin_kendaraan_create(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    if request.method == 'POST':
        form = KendaraanAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Kendaraan berhasil ditambahkan.")
            return redirect('admin_kendaraan_list')
    else:
        form = KendaraanAdminForm()
    return render(request, 'manajemen_pengguna/admin_kendaraan_form.html', {'form': form, 'mode': 'create'})


@login_required(login_url='login')
def admin_kendaraan_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    if request.method == 'POST':
        form = KendaraanAdminForm(request.POST, request.FILES, instance=kendaraan)
        if form.is_valid():
            form.save()
            messages.success(request, "Kendaraan berhasil diperbarui.")
            return redirect('admin_kendaraan_list')
    else:
        form = KendaraanAdminForm(instance=kendaraan)
    return render(request, 'manajemen_pengguna/admin_kendaraan_form.html', {'form': form, 'mode': 'update', 'kendaraan': kendaraan})


@login_required(login_url='login')
def admin_kendaraan_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    if request.method == 'POST':
        kendaraan.delete()
        messages.success(request, "Kendaraan berhasil dihapus.")
        return redirect('admin_kendaraan_list')
    return render(request, 'manajemen_pengguna/admin_kendaraan_confirm_delete.html', {'kendaraan': kendaraan})


# ==========================================
# 6. CRUD RESERVASI (Admin)
# ==========================================
@login_required(login_url='login')
def admin_reservasi_list(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    reservasi_list = Reservasi.objects.select_related('pelanggan', 'kendaraan').order_by('-id')
    return render(request, 'manajemen_pengguna/admin_reservasi_list.html', {'reservasi_list': reservasi_list})


@login_required(login_url='login')
def admin_reservasi_create(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    if request.method == 'POST':
        form = ReservasiAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservasi berhasil dibuat.")
            return redirect('admin_reservasi_list')
    else:
        form = ReservasiAdminForm()
    return render(request, 'manajemen_pengguna/admin_reservasi_form.html', {'form': form, 'mode': 'create'})


@login_required(login_url='login')
def admin_reservasi_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    reservasi = get_object_or_404(Reservasi, pk=pk)
    if request.method == 'POST':
        form = ReservasiAdminForm(request.POST, instance=reservasi)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservasi berhasil diperbarui.")
            return redirect('admin_reservasi_list')
    else:
        form = ReservasiAdminForm(instance=reservasi)
    return render(request, 'manajemen_pengguna/admin_reservasi_form.html', {'form': form, 'mode': 'update', 'reservasi': reservasi})


@login_required(login_url='login')
def admin_reservasi_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    reservasi = get_object_or_404(Reservasi, pk=pk)
    if request.method == 'POST':
        reservasi.delete()
        messages.success(request, "Reservasi berhasil dihapus.")
        return redirect('admin_reservasi_list')
    return render(request, 'manajemen_pengguna/admin_reservasi_confirm_delete.html', {'reservasi': reservasi})


# ==========================================
# 7. CRUD TAGIHAN (Admin)
# ==========================================
@login_required(login_url='login')
def admin_tagihan_list(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    tagihan_list = Tagihan.objects.select_related('reservasi', 'reservasi__pelanggan', 'reservasi__kendaraan').order_by('-id')
    return render(request, 'manajemen_pengguna/admin_tagihan_list.html', {'tagihan_list': tagihan_list})


@login_required(login_url='login')
def admin_tagihan_create(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    if request.method == 'POST':
        form = TagihanAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tagihan berhasil dibuat.")
            return redirect('admin_tagihan_list')
    else:
        form = TagihanAdminForm()
    return render(request, 'manajemen_pengguna/admin_tagihan_form.html', {'form': form, 'mode': 'create'})


@login_required(login_url='login')
def admin_tagihan_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    tagihan = get_object_or_404(Tagihan, pk=pk)
    if request.method == 'POST':
        form = TagihanAdminForm(request.POST, instance=tagihan)
        if form.is_valid():
            form.save()
            messages.success(request, "Tagihan berhasil diperbarui.")
            return redirect('admin_tagihan_list')
    else:
        form = TagihanAdminForm(instance=tagihan)
    return render(request, 'manajemen_pengguna/admin_tagihan_form.html', {'form': form, 'mode': 'update', 'tagihan': tagihan})


@login_required(login_url='login')
def admin_tagihan_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    tagihan = get_object_or_404(Tagihan, pk=pk)
    if request.method == 'POST':
        tagihan.delete()
        messages.success(request, "Tagihan berhasil dihapus.")
        return redirect('admin_tagihan_list')
    return render(request, 'manajemen_pengguna/admin_tagihan_confirm_delete.html', {'tagihan': tagihan})


# ==========================================
# 8. CRUD PENGGUNA (Admin)
# ==========================================
@login_required(login_url='login')
def admin_pengguna_list(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    pengguna_list = User.objects.filter(is_superuser=False).select_related('profil').order_by('username')
    # Pastikan profil tersedia agar template aman
    for user in pengguna_list:
        ProfilPengguna.objects.get_or_create(user=user)
    return render(request, 'manajemen_pengguna/admin_pengguna_list.html', {'pengguna_list': pengguna_list})


@login_required(login_url='login')
def admin_pengguna_create(request):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    if request.method == 'POST':
        form = UserAdminCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pengguna berhasil dibuat.")
            return redirect('admin_pengguna_list')
    else:
        form = UserAdminCreateForm()
    return render(request, 'manajemen_pengguna/admin_pengguna_form.html', {'form': form, 'mode': 'create'})


@login_required(login_url='login')
def admin_pengguna_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    pengguna = get_object_or_404(User, pk=pk, is_superuser=False)
    profil = getattr(pengguna, 'profil', None)
    if request.method == 'POST':
        form = UserAdminUpdateForm(request.POST, instance=pengguna, profil=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Pengguna berhasil diperbarui.")
            return redirect('admin_pengguna_list')
    else:
        form = UserAdminUpdateForm(instance=pengguna, profil=profil)
    return render(request, 'manajemen_pengguna/admin_pengguna_form.html', {'form': form, 'mode': 'update', 'pengguna': pengguna})


@login_required(login_url='login')
def admin_pengguna_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('home')
    pengguna = get_object_or_404(User, pk=pk, is_superuser=False)
    if pengguna == request.user:
        messages.error(request, "Anda tidak dapat menghapus akun sendiri.")
        return redirect('admin_pengguna_list')
    if request.method == 'POST':
        pengguna.delete()
        messages.success(request, "Pengguna berhasil dihapus.")
        return redirect('admin_pengguna_list')
    return render(request, 'manajemen_pengguna/admin_pengguna_confirm_delete.html', {'pengguna': pengguna})