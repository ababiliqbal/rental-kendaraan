from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Import Model
from kendaraan_ext.models import Kendaraan
from .models import Reservasi, Tagihan, Pembayaran
from .forms import RegistrasiPelangganForm, ReservasiForm, PembayaranForm, EditProfilForm

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

@login_required(login_url='login')
def profil_view(request):
    profil = request.user.profil  # Ambil data profil user yg login
    
    if request.method == 'POST':
        form = EditProfilForm(request.POST, instance=profil)
        if form.is_valid():
            # 1. Simpan data ProfilPengguna
            form.save()
            
            # 2. Simpan data User (Nama & Email)
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            messages.success(request, "Profil berhasil diperbarui!")
            return redirect('profil')
    else:
        # Pre-fill form dengan data saat ini
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        form = EditProfilForm(instance=profil, initial=initial_data)

    return render(request, 'manajemen_pengguna/profil.html', {'form': form})

@login_required(login_url='login')
def ganti_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash penting agar user TIDAK ter-logout otomatis
            update_session_auth_hash(request, user)  
            messages.success(request, 'Password berhasil diperbarui!')
            return redirect('profil')
        else:
            messages.error(request, 'Gagal mengganti password. Periksa kesalahan di bawah.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'manajemen_pengguna/ganti_password.html', {'form': form})