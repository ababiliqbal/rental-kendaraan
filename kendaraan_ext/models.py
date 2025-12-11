from django.db import models

# ==========================================
# 0. MITRA (New Model - Vendor Management)
# ==========================================
class Mitra(models.Model):
    nama = models.CharField(max_length=100)
    no_hp = models.CharField(max_length=20)
    alamat = models.TextField(blank=True)
    keterangan = models.TextField(blank=True, help_text="Catatan khusus kontrak mitra")

    def __str__(self):
        return self.nama

# ==========================================
# 1. KENDARAAN (Induk / Base Model)
# ==========================================
class Kendaraan(models.Model):
    STATUS_CHOICES = [
        ("Tersedia", "Tersedia"),
        ("Dirental", "Dirental"),
        ("Perawatan", "Perawatan"),
    ]

    # Atribut Dasar
    plat_nomor = models.CharField(max_length=20, unique=True)
    merk = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    tahun = models.PositiveIntegerField()
    harga_sewa_per_hari = models.PositiveIntegerField()
    
    # Atribut Status & Gambar
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Tersedia")
    gambar = models.ImageField(upload_to='kendaraan/', blank=True, null=True)

    # Atribut Kemitraan (Relational Update)
    # Jika mitra kosong (null), berarti milik perusahaan sendiri
    mitra = models.ForeignKey(
        Mitra, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='list_kendaraan',
        help_text="Kosongkan jika kendaraan ini milik perusahaan sendiri (Aset Internal)"
    )
    persentase_mitra = models.IntegerField(
        default=0, 
        help_text="Berapa % bagi hasil untuk mitra? (Contoh: 70)"
    )

    class Meta:
        verbose_name = "Kendaraan"
        verbose_name_plural = "Daftar Kendaraan"

    def __str__(self):
        # Tambahkan label [MITRA] otomatis jika ada pemiliknya
        prefix = f"[MITRA: {self.mitra.nama}] " if self.mitra else ""
        return f"{prefix}{self.merk} {self.model} ({self.plat_nomor})"
    
    # Helper Property untuk mengecek status kepemilikan di Template/Views
    @property
    def is_mitra(self):
        return self.mitra is not None

    @property
    def cek_mobil(self):
        try:
            return self.detail_mobil
        except:
            return None

    @property
    def cek_motor(self):
        try:
            return self.detail_motor
        except:
            return None

# ==========================================
# 2. EXTENSION MODELS (Mobil & Motor)
# ==========================================

class KendaraanExt(models.Model):
    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Ext: {self.kendaraan}"

class Mobil(models.Model):
    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE, related_name='detail_mobil')
    jumlah_kursi = models.PositiveIntegerField()
    transmisi = models.CharField(max_length=20)

    def __str__(self):
        return f"Mobil: {self.kendaraan.model} ({self.transmisi})"

class Motor(models.Model):
    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE, related_name='detail_motor')
    tipe_motor = models.CharField(max_length=30)
    kapasitas_mesin_cc = models.PositiveIntegerField()

    def __str__(self):
        return f"Motor: {self.kendaraan.model} ({self.kapasitas_mesin_cc}cc)"

class Garasi(models.Model):
    lokasi = models.CharField(max_length=100)
    kendaraan = models.ManyToManyField(Kendaraan)

    def __str__(self):
        return self.lokasi

    def jumlah_kendaraan(self):
        return self.kendaraan.count()