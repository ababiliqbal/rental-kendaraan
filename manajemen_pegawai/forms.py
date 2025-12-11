from django import forms
from django.contrib.auth.models import User
from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan


class PegawaiForm(forms.ModelForm):
    """Form kustom untuk create/update data pegawai, 
    menggabungkan field User (first_name, last_name, email) dan Pegawai."""
    
    # Tambahan field untuk Model User (ini TIDAK ada di Model Pegawai)
    first_name = forms.CharField(
        max_length=150, # Disesuaikan dengan max_length di Model User bawaan
        label="Nama Depan",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150, # Disesuaikan dengan max_length di Model User bawaan
        label="Nama Belakang",
        required=False, # Opsional di User Model
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Pegawai
        
        # KUNCI: Gabungkan Field User yang ditambahkan secara manual 
        # dengan semua field dari Pegawai (kecuali 'user', 'created_at', 'updated_at')
        fields = [
            'first_name', 'last_name', 'email',  # <--- Field User
            'no_induk_pegawai', 'no_ktp', 'no_telepon', 'alamat', 
            'jabatan', 'departemen', 'tanggal_bergabung', 'gaji_pokok', 
            'status'
        ] 
        
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
    """Form untuk create/update jadwal kerja, dilengkapi validasi overlap."""
    
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
        """
        Melakukan validasi utama, termasuk pengecekan tumpang tindih tanggal.
        """
        cleaned_data = super().clean()
        pegawai = cleaned_data.get('pegawai')
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')
        
        # --- Pengecekan 1: Tanggal Mulai dan Selesai ---
        if tanggal_mulai and tanggal_selesai and tanggal_mulai > tanggal_selesai:
             raise ValidationError(
                'Tanggal mulai tidak boleh melebihi tanggal selesai.',
                code='invalid_date_range'
            )
            
        # Pengecekan tumpang tindih hanya dilakukan jika pegawai dan tanggal mulai ada
        if pegawai and tanggal_mulai:
            
            # Mendapatkan ID instance yang sedang diedit (jika ada), agar instance itu sendiri dikecualikan dari pengecekan
            instance_id = self.instance.pk 
            
            # --- Pengecekan 2: Overlap Jadwal ---
            
            # 1. Kasus Tumpang Tindih dengan Jadwal yang Berakhir
            # Cari jadwal yang TANGGAL SELESAI-nya sudah ditetapkan
            overlap_queryset = JadwalKerja.objects.filter(
                pegawai=pegawai,
                tanggal_mulai__lte=tanggal_selesai if tanggal_selesai else tanggal_mulai, # Jadwal overlap dimulai sebelum atau pada akhir jadwal baru
                tanggal_selesai__gte=tanggal_mulai,                                        # Jadwal overlap berakhir setelah atau pada awal jadwal baru
            ).exclude(pk=instance_id)

            # 2. Kasus Tumpang Tindih dengan Jadwal yang Tidak Berakhir (Open-ended)
            # Cari jadwal yang TANGGAL SELESAI-nya NULL (berlaku tanpa batas)
            if tanggal_selesai:
                # Jika jadwal baru berakhir, cek jadwal tanpa batas yang dimulai sebelum akhir jadwal baru
                overlap_queryset_null = JadwalKerja.objects.filter(
                    pegawai=pegawai,
                    tanggal_selesai__isnull=True,
                    tanggal_mulai__lte=tanggal_selesai # Jadwal tanpa batas dimulai sebelum atau pada akhir jadwal baru
                ).exclude(pk=instance_id)
                overlap_queryset |= overlap_queryset_null
            else:
                # Jika jadwal baru juga tanpa batas (tanggal_selesai=None), cek jadwal tanpa batas lainnya
                overlap_queryset_null = JadwalKerja.objects.filter(
                    pegawai=pegawai,
                    tanggal_selesai__isnull=True,
                ).exclude(pk=instance_id)
                overlap_queryset |= overlap_queryset_null
            
            if overlap_queryset.exists():
                raise ValidationError(
                    'Jadwal pegawai ini tumpang tindih dengan jadwal lain yang sudah ada.',
                    code='schedule_overlap'
                )

        return cleaned_data


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