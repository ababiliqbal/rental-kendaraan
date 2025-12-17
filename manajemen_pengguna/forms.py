from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput
from .models import ProfilPengguna, Reservasi, Pembayaran
from django.core.exceptions import ValidationError
from manajemen_pegawai.models import Pegawai

def validate_file_size(value):
    filesize = value.size
    limit_mb = 2
    if filesize > limit_mb * 1024 * 1024:
        raise ValidationError(f"Ukuran file terlalu besar! Maksimal {limit_mb}MB.")

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
        # [UPDATE] Menambahkan field sopir ke sini
        fields = ['tgl_mulai', 'tgl_selesai', 'pakai_supir', 'supir']
        
        widgets = {
            'tgl_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tgl_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Widget khusus untuk Sopir (agar terbaca oleh JavaScript di HTML)
            'pakai_supir': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_pakai_supir'}),
            'supir': forms.Select(attrs={'class': 'form-select', 'id': 'id_supir'}),
        }
        
        labels = {
            'pakai_supir': 'Gunakan Jasa Sopir (+ Rp 150.000/hari)',
            'supir': 'Pilih Sopir (Kosongkan jika ingin dipilihkan sistem)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # [LOGIC] Filter dropdown hanya menampilkan pegawai 'Driver' & 'Aktif'
        # Query ini sekarang aman karena kita sudah import Pegawai di atas
        self.fields['supir'].queryset = Pegawai.objects.filter(jabatan='Driver', status='Aktif')
        self.fields['supir'].required = False  # Boleh kosong (untuk fitur Auto-Assign)
        self.fields['supir'].empty_label = "--- Pilihkan Saya Sopir Otomatis ---"

class PembayaranForm(forms.ModelForm):
    bukti_transfer = forms.ImageField(
        required=True,
        label="Upload Bukti Transfer",
        # Validator keamanan kita pasang di sini
        validators=[validate_file_size],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*' # UX: Memfilter agar user hanya bisa pilih gambar di file explorer
        })
    )

    class Meta:
        model = Pembayaran
        fields = ['jumlah', 'bukti_transfer']
        widgets = {
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
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