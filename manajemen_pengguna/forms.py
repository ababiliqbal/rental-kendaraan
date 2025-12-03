from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput
from .models import ProfilPengguna, Reservasi, Pembayaran

class RegistrasiPelangganForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Nama Depan", required=True)
    last_name = forms.CharField(label="Nama Belakang", required=True)
    
    no_ktp = forms.CharField(max_length=20, label="Nomor KTP")
    no_sim = forms.CharField(max_length=20, label="Nomor SIM")
    no_telepon = forms.CharField(max_length=15, label="Nomor Telepon")
    alamat = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Alamat")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

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
        fields = ['jumlah', 'bukti_transfer']
        widgets = {
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'bukti_transfer': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EditProfilForm(forms.ModelForm):
    # Kita ambil field dari User (Nama Depan, Belakang, Email)
    first_name = forms.CharField(label="Nama Depan", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nama Belakang", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    # Field dari ProfilPengguna
    no_ktp = forms.CharField(label="Nomor KTP", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_sim = forms.CharField(label="Nomor SIM", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_telepon = forms.CharField(label="Nomor Telepon", widget=forms.TextInput(attrs={'class': 'form-control'}))
    alamat = forms.CharField(label="Alamat", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = ProfilPengguna
        fields = ['no_ktp', 'no_sim', 'no_telepon', 'alamat']