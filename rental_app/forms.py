# rental_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import ProfilPengguna
from django.forms import DateInput
from .models import Reservasi
from .models import Pembayaran

class RegistrasiPelangganForm(forms.ModelForm):
    # Field tambahan untuk User bawaan Django
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Nama Depan", required=True)
    last_name = forms.CharField(label="Nama Belakang", required=True)

    # Field tambahan dari model ProfilPengguna
    no_ktp = forms.CharField(max_length=20, label="Nomor KTP")
    no_sim = forms.CharField(max_length=20, label="Nomor SIM")
    no_telepon = forms.CharField(max_length=15, label="Nomor Telepon")
    alamat = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Alamat")

    class Meta:
        model = User
        # Field yang akan disimpan ke tabel User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    # rental_app/forms.py

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            ProfilPengguna.objects.create(
                user=user,
                no_ktp=self.cleaned_data['no_ktp'],
                no_sim=self.cleaned_data['no_sim'],
                no_telepon=self.cleaned_data['no_telepon'],
                alamat=self.cleaned_data['alamat'],
                
                is_pegawai=False 
            )
        return user

class ReservasiForm(forms.ModelForm):
    class Meta:
        model = Reservasi
        fields = ['tgl_mulai', 'tgl_selesai']
        widgets = {
            'tgl_mulai': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tgl_selesai': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = ['jumlah', 'bukti_transfer'] # User input jumlah & bukti
        widgets = {
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Readonly biar gak curang
            'bukti_transfer': forms.FileInput(attrs={'class': 'form-control'}),
        }