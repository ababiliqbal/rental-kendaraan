from django import forms
from django.contrib.auth.models import User
from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan


class PegawaiForm(forms.ModelForm):
    """Form untuk create/update data pegawai"""
    # Tambahan field untuk User
    first_name = forms.CharField(
        max_length=30,
        label="Nama Depan",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Nama Belakang",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Pegawai
        fields = ['no_induk_pegawai', 'no_ktp', 'no_telepon', 'alamat', 
                  'jabatan', 'departemen', 'tanggal_bergabung', 'gaji_pokok', 'status']
        widgets = {
            'no_induk_pegawai': forms.TextInput(attrs={'class': 'form-control'}),
            'no_ktp': forms.TextInput(attrs={'class': 'form-control'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'jabatan': forms.Select(attrs={'class': 'form-control'}),
            'departemen': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_bergabung': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gaji_pokok': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        """Override save untuk update User object juga"""
        pegawai = super().save(commit=False)
        # Update related User object
        pegawai.user.first_name = self.cleaned_data['first_name']
        pegawai.user.last_name = self.cleaned_data['last_name']
        pegawai.user.email = self.cleaned_data['email']
        
        if commit:
            pegawai.user.save()
            pegawai.save()
        return pegawai


class ShiftForm(forms.ModelForm):
    """Form untuk create/update shift"""
    class Meta:
        model = Shift
        fields = ['nama_shift', 'jam_mulai', 'jam_selesai', 'tunjangan_shift']
        widgets = {
            'nama_shift': forms.Select(attrs={'class': 'form-control'}),
            'jam_mulai': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'jam_selesai': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'tunjangan_shift': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class JadwalKerjaForm(forms.ModelForm):
    """Form untuk create/update jadwal kerja"""
    class Meta:
        model = JadwalKerja
        fields = ['pegawai', 'shift', 'tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'pegawai': forms.Select(attrs={'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class HistoriKerjaPegawaiForm(forms.ModelForm):
    """Form untuk create histori kerja"""
    class Meta:
        model = HistoriKerjaPegawai
        fields = ['pegawai', 'tipe_aktivitas', 'tanggal_waktu', 'keterangan']
        widgets = {
            'pegawai': forms.Select(attrs={'class': 'form-control'}),
            'tipe_aktivitas': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_waktu': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GajiPegawaiForm(forms.ModelForm):
    """Form untuk create/update slip gaji"""
    class Meta:
        model = GajiPegawai
        fields = ['pegawai', 'bulan', 'gaji_pokok', 'tunjangan', 'potongan', 'status', 'tanggal_pembayaran']
        widgets = {
            'pegawai': forms.Select(attrs={'class': 'form-control'}),
            'bulan': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gaji_pokok': forms.NumberInput(attrs={'class': 'form-control'}),
            'tunjangan': forms.NumberInput(attrs={'class': 'form-control'}),
            'potongan': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_pembayaran': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PenghargaanForm(forms.ModelForm):
    """Form untuk create penghargaan"""
    class Meta:
        model = Penghargaan
        fields = ['pegawai', 'tipe', 'nominal', 'tanggal', 'keterangan']
        widgets = {
            'pegawai': forms.Select(attrs={'class': 'form-control'}),
            'tipe': forms.Select(attrs={'class': 'form-control'}),
            'nominal': forms.NumberInput(attrs={'class': 'form-control'}),
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }