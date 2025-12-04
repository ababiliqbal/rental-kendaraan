from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Kita import Kendaraan dari app sebelah
from kendaraan_ext.models import Kendaraan

# ==========================================
# 1. PROFIL PENGGUNA
# ==========================================
class ProfilPengguna(models.Model):
    """Model untuk profil pelanggan rental kendaraan"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    
    # Data Diri Pelanggan
    no_ktp = models.CharField(max_length=20, blank=True, null=True)
    no_sim = models.CharField(max_length=20, blank=True, null=True)
    no_telepon = models.CharField(max_length=15, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Pengguna"
        verbose_name_plural = "Profil Pengguna"
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Pelanggan)"

# ==========================================
# 2. RESERVASI (Transaksi Booking)
# ==========================================
class Reservasi(models.Model):
    STATUS_RESERVASI = [
        ('Dipesan', 'Dipesan'),   # Baru booking, belum bayar/belum diambil
        ('Aktif', 'Aktif'),       # Mobil sedang dibawa pelanggan
        ('Selesai', 'Selesai'),   # Mobil sudah dikembalikan
        ('Batal', 'Batal'),       # Dibatalkan user/admin
    ]

    # Relasi
    pelanggan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservasi_saya')
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE)
    
    # Detail Sewa
    tgl_mulai = models.DateField()
    tgl_selesai = models.DateField()
    tgl_pengembalian_aktual = models.DateField(null=True, blank=True)
    
    # Biaya (Disimpan statis agar tidak berubah kalau harga mobil naik)
    total_biaya = models.DecimalField(max_digits=12, decimal_places=0)
    
    status = models.CharField(max_length=15, choices=STATUS_RESERVASI, default='Dipesan')
    created_at = models.DateTimeField(auto_now_add=True)

    def hitung_durasi(self):
        return (self.tgl_selesai - self.tgl_mulai).days
    
    @property
    def cek_tagihan(self):
        try:
            return self.tagihan
        except:
            return None
    
    def __str__(self):
        return f"Booking #{self.id} - {self.pelanggan.username}"

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
    
    def __str__(self):
        return f"Bayar Rp {self.jumlah} - {self.metode}"