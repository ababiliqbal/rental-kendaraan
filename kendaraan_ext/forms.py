# kendaraan/forms.py

from django import forms
from .models import Kendaraan, Mobil, Motor

class KendaraanForm(forms.ModelForm):
    # ... (Isi class Meta untuk model Kendaraan) ...
    class Meta:
        model = Kendaraan
        fields = ['plat_nomor', 'merk', 'model', 'tahun', 'harga_sewa_per_hari', 
                  'status', 'gambar', 'tipe_kepemilikan', 'id_mitra', 
                  'persen_bagi_hasil']

class MobilForm(forms.ModelForm):
    # ... (Isi class Meta untuk model Mobil) ...
    class Meta:
        model = Mobil
        fields = ['jumlah_kursi', 'transmisi']

class MotorForm(forms.ModelForm):
    # ... (Isi class Meta untuk model Motor) ...
    class Meta:
        model = Motor
        fields = ['tipe_motor', 'kapasitas_mesin_cc']

# --- TAMBAHAN UNTUK GARASI ---
from .models import Garasi 

class GarasiForm(forms.ModelForm):
    # Kita menggunakan widget CheckboxSelectMultiple untuk ManyToManyField kendaraan
    kendaraan = forms.ModelMultipleChoiceField(
        queryset=Kendaraan.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Garasi
        fields = ['lokasi', 'kendaraan']