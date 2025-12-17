from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Import Model
from kendaraan_ext.models import Kendaraan
from .models import Reservasi, Tagihan, Pembayaran, ProfilPengguna
from .forms import RegistrasiPelangganForm, ReservasiForm, PembayaranForm, EditProfilForm
from manajemen_pegawai.models import Pegawai

# ==========================================
# 1. HALAMAN UTAMA (HOME)
# ==========================================
def home(request):
    query = request.GET.get('q')          
    kategori = request.GET.get('kategori')

    kendaraan_list = Kendaraan.objects.filter(status='Tersedia').order_by('-id')

    if kategori == 'mobil':

        kendaraan_list = kendaraan_list.filter(detail_mobil__isnull=False)
    elif kategori == 'motor':

        kendaraan_list = kendaraan_list.filter(detail_motor__isnull=False)

    if query:

        kendaraan_list = kendaraan_list.filter(
            Q(merk__icontains=query) | 
            Q(model__icontains=query) |
            Q(plat_nomor__icontains=query)
        )

    context = {
        'kendaraan_list': kendaraan_list,
        'request_q': query, 
        'request_kategori': kategori
    }
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
            
            # [PERBAIKAN LOGIKA DURASI]
            # Menghitung selisih hari
            durasi = (reservasi.tgl_selesai - reservasi.tgl_mulai).days
            
            # Jika tanggal terbalik (Minus) -> ERROR
            if durasi < 0:
                messages.error(request, "Tanggal selesai tidak boleh sebelum tanggal mulai!")
                return render(request, 'manajemen_pengguna/booking_form.html', {'form': form, 'mobil': mobil})
            
            # Jika tanggal sama (0 hari) -> Dianggap 1 Hari, Lanjut!
            
            # ====================================================
            # [LOGIKA BARU] SISTEM MANAJEMEN SOPIR & CEK BENTROK
            # ====================================================
            if reservasi.pakai_supir:
                # Cari ID Sopir yang sedang SIBUK di rentang tanggal tersebut
                supir_sibuk_ids = Reservasi.objects.filter(
                    Q(status='Dipesan') | Q(status='Aktif'), 
                    tgl_mulai__lte=reservasi.tgl_selesai,
                    tgl_selesai__gte=reservasi.tgl_mulai,
                    supir__isnull=False
                ).values_list('supir_id', flat=True)

                # SKENARIO A: User Memilih Sopir Secara Manual
                if reservasi.supir:
                    if reservasi.supir.id in supir_sibuk_ids:
                        messages.error(request, f"Maaf, Sopir {reservasi.supir.user.first_name} sudah ada jadwal di tanggal tersebut.")
                        return render(request, 'manajemen_pengguna/booking_form.html', {'form': form, 'mobil': mobil})
                
                # SKENARIO B: User Minta Dipilihkan Otomatis (Hybrid Algorithm)
                else:
                    calon_supir = Pegawai.objects.filter(
                        jabatan='Driver', 
                        status='Aktif'
                    ).exclude(
                        id__in=supir_sibuk_ids
                    ).order_by(
                        '-rating',      # Prioritas 1: Rating TERTINGGI (Desc)
                        'jumlah_trip'   # Prioritas 2: Trip TERDIKIT (Asc) - untuk pemerataan
                    ).first()

                    if calon_supir:
                        reservasi.supir = calon_supir
                        
                        # [PENTING] Update statistik supir
                        calon_supir.jumlah_trip += 1
                        calon_supir.save()
                        
                        messages.info(request, f"Sistem merekomendasikan Top Rated Driver kami: {calon_supir.user.first_name} (⭐{calon_supir.rating})")
                    else:
                        messages.error(request, "Mohon maaf, semua sopir kami FULL BOOKED. Silakan pilih tanggal lain.")
                        return render(request, 'manajemen_pengguna/booking_form.html', {'form': form, 'mobil': mobil})
            
            # [TAMBAHAN SAFETY] Jika user tidak centang pakai sopir, pastikan data bersih
            else:
                reservasi.supir = None
                reservasi.biaya_supir = 0
            # ====================================================

            reservasi.status = 'Dipesan'
            
            # Simpan (Model akan menghitung total biaya otomatis)
            reservasi.save()
            
            # Buat Tagihan
            Tagihan.objects.create(reservasi=reservasi, total_akhir=reservasi.total_biaya)
            
            messages.success(request, f"Booking berhasil! Total Tagihan: Rp {reservasi.total_biaya:,.0f}")
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
    
    # Ambil tagihan
    tagihan, created = Tagihan.objects.get_or_create(
        reservasi=reservasi,
        defaults={'total_akhir': reservasi.total_biaya} 
    )
    
    # LOGIKA BARU: Hitung Sisa Bayar
    sisa_tagihan = tagihan.sisa_bayar()

    if request.method == 'POST':
        form = PembayaranForm(request.POST, request.FILES)
        if form.is_valid():
            pembayaran = form.save(commit=False)
            pembayaran.tagihan = tagihan
            pembayaran.metode = 'Transfer'
            
            # Validasi Logic: Jangan biarkan user bayar 0 atau negatif
            if pembayaran.jumlah <= 0:
                messages.error(request, "Jumlah pembayaran tidak valid.")
                return redirect('bayar', reservasi_id=reservasi.id)

            pembayaran.save()
            
            tagihan.status = 'Menunggu Verifikasi'
            tagihan.save()
            
            messages.success(request, "Bukti pembayaran berhasil dikirim!")
            return redirect('riwayat')
    else:
        # PRE-FILL FORM DENGAN SISA TAGIHAN (BUKAN TOTAL BIAYA LAGI)
        # Jika sisa < 0 (aneh), set 0. Jika > 0, set sisa.
        nilai_awal = sisa_tagihan if sisa_tagihan > 0 else 0
        form = PembayaranForm(initial={'jumlah': nilai_awal})

    context = {
        'form': form, 
        'reservasi': reservasi,
        'tagihan': tagihan,          # Kirim objek tagihan ke template
        'sisa_tagihan': sisa_tagihan # Kirim angka sisa ke template
    }
    return render(request, 'manajemen_pengguna/bayar_form.html', context)

@login_required(login_url='login')
def profil_view(request):
    profil, created = ProfilPengguna.objects.get_or_create(user=request.user)
    
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