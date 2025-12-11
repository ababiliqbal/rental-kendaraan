from django import forms
from kendaraan_ext.models import Kendaraan, Mobil, Motor, Mitra

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