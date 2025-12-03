from django.db import models

# ==========================================
# 1. KENDARAAN (Induk / Base Model)
# ==========================================
class Kendaraan(models.Model):
    STATUS_CHOICES = [
        ("Tersedia", "Tersedia"),
        ("Dirental", "Dirental"),
        ("Perawatan", "Perawatan"),
    ]

    KEPEMILIKAN_CHOICES = [
        ("Milik Sendiri", "Milik Sendiri"),
        ("Mitra", "Mitra"),
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

    # Atribut Kemitraan
    tipe_kepemilikan = models.CharField(max_length=20, choices=KEPEMILIKAN_CHOICES, default="Milik Sendiri")
    id_mitra = models.CharField(max_length=50, null=True, blank=True)
    persen_bagi_hasil = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Kendaraan"
        verbose_name_plural = "Daftar Kendaraan"

    def __str__(self):
        prefix = "[MITRA] " if self.tipe_kepemilikan == "Mitra" else ""
        return f"{prefix}{self.merk} {self.model} ({self.plat_nomor})"

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