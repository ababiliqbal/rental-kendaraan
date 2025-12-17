from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Kita import Kendaraan dari app sebelah
from kendaraan_ext.models import Kendaraan
from django.db.models import Sum
from manajemen_pegawai.models import Pegawai

# ==========================================
# 1. PROFIL PENGGUNA
# ==========================================
class ProfilPengguna(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    
    # Data Diri
    no_ktp = models.CharField(max_length=20, blank=True, null=True)
    no_sim = models.CharField(max_length=20, blank=True, null=True)
    no_telepon = models.CharField(max_length=15, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    
    # Role (Pegawai atau Bukan)
    is_pegawai = models.BooleanField(default=False)
    jabatan = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Pegawai' if self.is_pegawai else 'Pelanggan'}"

# ==========================================
# 2. RESERVASI (Transaksi Booking)
# ==========================================
class Reservasi(models.Model):
    STATUS_RESERVASI = [
        ('Dipesan', 'Dipesan'),
        ('Aktif', 'Aktif'),
        ('Selesai', 'Selesai'),
        ('Batal', 'Batal'),
    ]

    pelanggan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservasi_saya')
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE)
    
    tgl_mulai = models.DateField()
    tgl_selesai = models.DateField()
    tgl_pengembalian_aktual = models.DateField(null=True, blank=True)
    
    # [FIELD BARU - FITUR SOPIR]
    pakai_supir = models.BooleanField(default=False, verbose_name="Pakai Sopir?")
    
    # Relasi ke Sopir (Pegawai). limit_choices_to memastikan dropdown hanya menampilkan Driver
    supir = models.ForeignKey(
        Pegawai, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='riwayat_menyetir',
        limit_choices_to={'jabatan': 'Driver'} 
    )
    
    # Menyimpan nominal biaya sopir terpisah (untuk detail invoice)
    biaya_supir = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    # Total Biaya (Mobil + Sopir)
    total_biaya = models.DecimalField(max_digits=12, decimal_places=0)
    
    status = models.CharField(max_length=15, choices=STATUS_RESERVASI, default='Dipesan')
    created_at = models.DateTimeField(auto_now_add=True)

    def hitung_durasi(self):
        durasi = (self.tgl_selesai - self.tgl_mulai).days
        # Jika sewa dan kembali di hari yang sama, hitung 1 hari
        return durasi if durasi > 0 else 1
    
    @property
    def cek_tagihan(self):
        try:
            return self.tagihan
        except:
            return None

    def save(self, *args, **kwargs):
        # 1. Hitung Durasi
        durasi = self.hitung_durasi()
        
        # 2. Hitung Biaya Sewa Mobil Dasar
        biaya_mobil = self.kendaraan.harga_sewa_per_hari * durasi
        
        # 3. Hitung Biaya Sopir (Jika dicentang)
        # Konstanta harga sopir: Rp 150.000 / hari
        HARGA_SUPIR_PER_HARI = 150000

        if self.pakai_supir:
            self.biaya_supir = HARGA_SUPIR_PER_HARI * durasi
        else:
            self.biaya_supir = 0
            self.supir = None  # Pastikan sopir kosong jika tidak dipilih
            
        # 4. Update Total Biaya
        self.total_biaya = biaya_mobil + self.biaya_supir
        
        super().save(*args, **kwargs)

    def __str__(self):
        info_supir = " (With Driver)" if self.pakai_supir else " (Lepas Kunci)"
        return f"Booking #{self.id} - {self.pelanggan.username}{info_supir}"

# ==========================================
# 3. TAGIHAN & PEMBAYARAN
# ==========================================
class Tagihan(models.Model):
    # Status diperjelas agar tim Pegawai mudah memfilter
    STATUS_BAYAR = [
        ('Belum Lunas', 'Belum Lunas'),
        ('Menunggu Verifikasi', 'Menunggu Verifikasi'), # User sudah upload, Admin belum cek
        ('Lunas', 'Lunas')
    ]
    
    reservasi = models.OneToOneField(Reservasi, on_delete=models.CASCADE)
    total_denda = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_akhir = models.DecimalField(max_digits=12, decimal_places=0)
    
    status = models.CharField(max_length=20, choices=STATUS_BAYAR, default='Belum Lunas')
    
    def hitung_uang_masuk(self):
        total = self.riwayat_pembayaran.filter(is_valid=True).aggregate(Sum('jumlah'))['jumlah__sum']
        return total if total else 0

    def sisa_bayar(self):
        return self.total_akhir - self.hitung_uang_masuk()
    
    def __str__(self):
        return f"Tagihan #{self.id} ({self.status})"

class Pembayaran(models.Model):
    METODE_BAYAR = [('Tunai', 'Tunai'), ('Transfer', 'Transfer')]

    tagihan = models.ForeignKey(Tagihan, on_delete=models.CASCADE, related_name='riwayat_pembayaran')
    jumlah = models.DecimalField(max_digits=12, decimal_places=0)
    tanggal = models.DateTimeField(default=timezone.now)
    metode = models.CharField(max_length=10, choices=METODE_BAYAR)
    
    # Bukti Transfer (Penting buat tugasmu)
    bukti_transfer = models.ImageField(upload_to='bukti_bayar/', blank=True, null=True)
    
    # Validasi (Diisi oleh Admin/Pegawai nanti)
    diterima_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Bayar Rp {self.jumlah} - {self.metode}"
    
# manajemen_pengguna/models.py

# ... (kode class Pembayaran yang sudah ada) ...

class Denda(models.Model):
    tagihan = models.ForeignKey(Tagihan, on_delete=models.CASCADE, related_name='daftar_denda')
    jenis = models.CharField(max_length=50) # Contoh: "Keterlambatan", "Lecet Bumper"
    jumlah = models.DecimalField(max_digits=12, decimal_places=0)
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.jenis} - Rp {self.jumlah}"