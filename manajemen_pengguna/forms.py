from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput

from kendaraan_ext.models import Kendaraan
from .models import ProfilPengguna, Reservasi, Pembayaran, Tagihan

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


class KendaraanAdminForm(forms.ModelForm):
    class Meta:
        model = Kendaraan
        fields = [
            'plat_nomor',
            'merk',
            'model',
            'tahun',
            'harga_sewa_per_hari',
            'status',
            'gambar',
            'tipe_kepemilikan',
            'id_mitra',
            'persen_bagi_hasil',
        ]
        widgets = {
            'plat_nomor': forms.TextInput(attrs={'class': 'form-control'}),
            'merk': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'tahun': forms.NumberInput(attrs={'class': 'form-control'}),
            'harga_sewa_per_hari': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gambar': forms.FileInput(attrs={'class': 'form-control'}),
            'tipe_kepemilikan': forms.Select(attrs={'class': 'form-select'}),
            'id_mitra': forms.TextInput(attrs={'class': 'form-control'}),
            'persen_bagi_hasil': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ReservasiAdminForm(forms.ModelForm):
    class Meta:
        model = Reservasi
        fields = [
            'pelanggan',
            'kendaraan',
            'tgl_mulai',
            'tgl_selesai',
            'tgl_pengembalian_aktual',
            'total_biaya',
            'status',
        ]
        widgets = {
            'pelanggan': forms.Select(attrs={'class': 'form-select'}),
            'kendaraan': forms.Select(attrs={'class': 'form-select'}),
            'tgl_mulai': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tgl_selesai': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tgl_pengembalian_aktual': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_biaya': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class TagihanAdminForm(forms.ModelForm):
    class Meta:
        model = Tagihan
        fields = ['reservasi', 'total_denda', 'total_akhir', 'status']
        widgets = {
            'reservasi': forms.Select(attrs={'class': 'form-select'}),
            'total_denda': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_akhir': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class UserAdminCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Password")
    no_ktp = forms.CharField(max_length=20, required=False, label="Nomor KTP", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_sim = forms.CharField(max_length=20, required=False, label="Nomor SIM", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_telepon = forms.CharField(max_length=15, required=False, label="Nomor Telepon", widget=forms.TextInput(attrs={'class': 'form-control'}))
    alamat = forms.CharField(required=False, label="Alamat", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    is_pegawai = forms.BooleanField(required=False, label="Tandai sebagai pegawai")
    jabatan = forms.CharField(max_length=50, required=False, label="Jabatan", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = False
        if commit:
            user.save()
            ProfilPengguna.objects.update_or_create(
                user=user,
                defaults={
                    'no_ktp': self.cleaned_data.get('no_ktp'),
                    'no_sim': self.cleaned_data.get('no_sim'),
                    'no_telepon': self.cleaned_data.get('no_telepon'),
                    'alamat': self.cleaned_data.get('alamat'),
                    'is_pegawai': self.cleaned_data.get('is_pegawai', False),
                    'jabatan': self.cleaned_data.get('jabatan'),
                }
            )
        return user


class UserAdminUpdateForm(forms.ModelForm):
    no_ktp = forms.CharField(max_length=20, required=False, label="Nomor KTP", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_sim = forms.CharField(max_length=20, required=False, label="Nomor SIM", widget=forms.TextInput(attrs={'class': 'form-control'}))
    no_telepon = forms.CharField(max_length=15, required=False, label="Nomor Telepon", widget=forms.TextInput(attrs={'class': 'form-control'}))
    alamat = forms.CharField(required=False, label="Alamat", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    is_pegawai = forms.BooleanField(required=False, label="Tandai sebagai pegawai")
    jabatan = forms.CharField(max_length=50, required=False, label="Jabatan", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.profil = kwargs.pop('profil', None)
        super().__init__(*args, **kwargs)
        if self.profil:
            self.fields['no_ktp'].initial = self.profil.no_ktp
            self.fields['no_sim'].initial = self.profil.no_sim
            self.fields['no_telepon'].initial = self.profil.no_telepon
            self.fields['alamat'].initial = self.profil.alamat
            self.fields['is_pegawai'].initial = self.profil.is_pegawai
            self.fields['jabatan'].initial = self.profil.jabatan

    def save(self, commit=True):
        user = super().save(commit=commit)
        profil_obj, _ = ProfilPengguna.objects.get_or_create(user=user)
        profil_obj.no_ktp = self.cleaned_data.get('no_ktp')
        profil_obj.no_sim = self.cleaned_data.get('no_sim')
        profil_obj.no_telepon = self.cleaned_data.get('no_telepon')
        profil_obj.alamat = self.cleaned_data.get('alamat')
        profil_obj.is_pegawai = self.cleaned_data.get('is_pegawai', False)
        profil_obj.jabatan = self.cleaned_data.get('jabatan')
        if commit:
            profil_obj.save()
        return user