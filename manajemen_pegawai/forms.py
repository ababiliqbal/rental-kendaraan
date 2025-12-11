from django import forms
from kendaraan_ext.models import Kendaraan, Mobil, Motor, Mitra
from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class FormPengembalian(forms.Form):
    denda_kerusakan = forms.IntegerField(
        required=False, 
        initial=0, 
        label="Biaya Kerusakan (Rp)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    keterangan_kerusakan = forms.CharField(
        required=False, 
        label="Keterangan Kerusakan",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Misal: Bumper penyok, baret halus...'})
    )

class KendaraanForm(forms.ModelForm):
    class Meta:
        model = Kendaraan
        fields = ['plat_nomor', 'merk', 'model', 'tahun', 'harga_sewa_per_hari', 'gambar', 'status', 'mitra', 'persentase_mitra']
        widgets = {
            'plat_nomor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'B 1234 XYZ'}),
            'merk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Avanza'}),
            'tahun': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
            'harga_sewa_per_hari': forms.NumberInput(attrs={'class': 'form-control'}),
            'gambar': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'mitra': forms.Select(attrs={'class': 'form-select'}),
            'persentase_mitra': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

class MobilForm(forms.ModelForm):
    class Meta:
        model = Mobil
        fields = ['jumlah_kursi', 'transmisi']
        widgets = {
            'jumlah_kursi': forms.NumberInput(attrs={'class': 'form-control', 'min': 2}),
            'transmisi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manual/Matic'}),
        }

class MotorForm(forms.ModelForm):
    class Meta:
        model = Motor
        fields = ['tipe_motor', 'kapasitas_mesin_cc']
        widgets = {
            'tipe_motor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matic/Sport/Bebek'}),
            'kapasitas_mesin_cc': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '150'}),
        }

class MitraForm(forms.ModelForm):
    class Meta:
        model = Mitra
        fields = ['nama', 'no_hp', 'alamat', 'keterangan']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Pak Budi Santoso'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0812xxxx'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan khusus...'}),
        }

# ==========================================
# FORMULIR MANAJEMEN PEGAWAI (FITUR BARU)
# ==========================================

class PegawaiForm(forms.ModelForm):
    """Form untuk create/update data pegawai + user"""
    first_name = forms.CharField(max_length=150, label="Nama Depan", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, label="Nama Belakang", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Pegawai
        fields = ['first_name', 'last_name', 'email', 'no_induk_pegawai', 'no_ktp', 'no_telepon', 'alamat', 'jabatan', 'departemen', 'tanggal_bergabung', 'gaji_pokok', 'status'] 
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

class ShiftForm(forms.ModelForm):
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
    class Meta:
        model = JadwalKerja
        fields = ['pegawai', 'shift', 'tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'pegawai': forms.Select(attrs={'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pegawai = cleaned_data.get('pegawai')
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')
        
        if tanggal_mulai and tanggal_selesai and tanggal_mulai > tanggal_selesai:
             raise ValidationError('Tanggal mulai tidak boleh melebihi tanggal selesai.', code='invalid_date_range')
            
        if pegawai and tanggal_mulai:
            instance_id = self.instance.pk 
            overlap_queryset = JadwalKerja.objects.filter(
                pegawai=pegawai,
                tanggal_mulai__lte=tanggal_selesai if tanggal_selesai else tanggal_mulai,
                tanggal_selesai__gte=tanggal_mulai,
            ).exclude(pk=instance_id)

            if tanggal_selesai:
                overlap_queryset_null = JadwalKerja.objects.filter(
                    pegawai=pegawai,
                    tanggal_selesai__isnull=True,
                    tanggal_mulai__lte=tanggal_selesai
                ).exclude(pk=instance_id)
                overlap_queryset |= overlap_queryset_null
            else:
                overlap_queryset_null = JadwalKerja.objects.filter(
                    pegawai=pegawai,
                    tanggal_selesai__isnull=True,
                ).exclude(pk=instance_id)
                overlap_queryset |= overlap_queryset_null
            
            if overlap_queryset.exists():
                raise ValidationError('Jadwal pegawai ini tumpang tindih dengan jadwal lain.', code='schedule_overlap')
        return cleaned_data

class HistoriKerjaPegawaiForm(forms.ModelForm):
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