# rental_app/views.py
from django.shortcuts import render, redirect
from .models import Kendaraan
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrasiPelangganForm

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
    return render(request, 'rental_app/home.html', {'kendaraan_list': kendaraan_list})

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