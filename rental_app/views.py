# rental_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Kendaraan
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrasiPelangganForm
from django.contrib.auth.decorators import login_required
from .forms import ReservasiForm
from .models import Reservasi
from kendaraan_ext.models import Kendaraan
from .forms import PembayaranForm
from .models import Tagihan, Pembayaran

def register_pelanggan(request):
    if request.method == 'POST':
        form = RegistrasiPelangganForm(request.POST)
        if form.is_valid():
            form.save() # Simpan user & profil ke database
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login') # Nanti kita arahkan ke halaman login
    else:
        # Jika user baru membuka halaman (GET)
        form = RegistrasiPelangganForm()

    return render(request, 'rental_app/register.html', {'form': form})

def home(request):
    kendaraan_list = Kendaraan.objects.filter(status='Tersedia')
    
    context = {
        'kendaraan_list': kendaraan_list
    }
    return render(request, 'rental_app/home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang kembali, {username}!")
                return redirect('home') # Nanti kita ubah ke 'dashboard'
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Username atau password tidak valid.")
    else:
        form = AuthenticationForm()

    return render(request, 'rental_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Anda berhasil logout.")
    return redirect('login')

@login_required(login_url='login')
def booking_view(request, mobil_id):
    # 1. Ambil data mobil yang dipilih berdasarkan ID
    mobil = Kendaraan.objects.get(id=mobil_id)
    
    if request.method == 'POST':
        form = ReservasiForm(request.POST)
        if form.is_valid():
            # 2. Simpan sementara (jangan commit ke DB dulu)
            reservasi = form.save(commit=False)
            
            # 3. Lengkapi data otomatis
            reservasi.pelanggan = request.user
            reservasi.kendaraan = mobil
            
            # 4. Hitung Durasi & Biaya
            durasi = (reservasi.tgl_selesai - reservasi.tgl_mulai).days
            
            if durasi <= 0:
                messages.error(request, "Tanggal selesai harus lebih besar dari tanggal mulai!")
                return render(request, 'rental_app/booking_form.html', {'form': form, 'mobil': mobil})
                
            reservasi.total_biaya = durasi * mobil.harga_sewa_per_hari
            reservasi.status = 'Dipesan'
            
            # 5. Simpan Final
            reservasi.save()
            
            messages.success(request, f"Berhasil booking {mobil.merk} {mobil.model}! Total: Rp {reservasi.total_biaya:,}")
            return redirect('home') # Nanti kita arahkan ke halaman riwayat
    else:
        form = ReservasiForm()

    return render(request, 'rental_app/booking_form.html', {'form': form, 'mobil': mobil})

@login_required(login_url='login')
def riwayat_view(request):
    # Ambil reservasi milik user yang sedang login saja (filter)
    # Urutkan dari yang terbaru (-id atau -created_at)
    reservasi_list = Reservasi.objects.filter(pelanggan=request.user).order_by('-id')
    
    context = {
        'reservasi_list': reservasi_list
    }
    return render(request, 'rental_app/riwayat.html', context)

@login_required(login_url='login')
def bayar_view(request, reservasi_id):
    # Ambil reservasi milik user
    reservasi = get_object_or_404(Reservasi, id=reservasi_id, pelanggan=request.user)
    
    # Cek/Buat Tagihan (Auto-generate tagihan jika belum ada)
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
            
            # Update status tagihan (Sederhana dulu)
            # Nanti Pegawai yang validasi lunas/belum
            messages.success(request, "Bukti transfer berhasil diupload! Tunggu verifikasi admin.")
            return redirect('riwayat')
    else:
        # Pre-fill jumlah bayar sesuai total biaya
        form = PembayaranForm(initial={'jumlah': reservasi.total_biaya})

    return render(request, 'rental_app/bayar_form.html', {'form': form, 'reservasi': reservasi})