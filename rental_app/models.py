from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#  KENDARAAN
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

    plat_nomor = models.CharField(max_length=20, unique=True)
    merk = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    tahun = models.PositiveIntegerField()
    harga_sewa_per_hari = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Tersedia"
    )

    tipe_kepemilikan = models.CharField(
        max_length=20,
        choices=KEPEMILIKAN_CHOICES,
        default="Milik Sendiri"
    )
    id_mitra = models.CharField(max_length=50, null=True, blank=True)
    persen_bagi_hasil = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Kendaraan"
        verbose_name_plural = "Daftar Kendaraan"

    def __str__(self):
        prefix = "[MITRA] " if self.tipe_kepemilikan == "Mitra" else ""
        return f"{prefix}{self.merk} {self.model} ({self.plat_nomor}) - {self.status}"


# MOBIL
class Mobil(Kendaraan):
    jumlah_kursi = models.PositiveIntegerField()
    transmisi = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Mobil"
        verbose_name_plural = "Daftar Mobil"

    def __str__(self):
        return f"{super().__str__()} | Kursi: {self.jumlah_kursi} | Transmisi: {self.transmisi}"


# MOTOR
class Motor(Kendaraan):
    tipe_motor = models.CharField(max_length=30)
    kapasitas_mesin_cc = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Motor"
        verbose_name_plural = "Daftar Motor"

    def __str__(self):
        return f"{super().__str__()} | Tipe: {self.tipe_motor} | CC: {self.kapasitas_mesin_cc}"

# GARASI
class Garasi(models.Model):
    lokasi = models.CharField(max_length=100)
    kendaraan = models.ManyToManyField(Kendaraan)

    class Meta:
        verbose_name = "Garasi"
        verbose_name_plural = "Daftar Garasi"

    def __str__(self):
        return self.lokasi

    def jumlah_kendaraan(self):
        return self.kendaraan.count()
    

class ProfilPengguna(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    
    no_telepon = models.CharField(max_length=15, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    
    no_ktp = models.CharField(max_length=20, blank=True, null=True)
    no_sim = models.CharField(max_length=20, blank=True, null=True)
    
    is_pegawai = models.BooleanField(default=False)
    jabatan = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        role = "Pegawai" if self.is_pegawai else "Pelanggan"
        return f"{self.user.username} ({role})"

class Kendaraan(models.Model):
    JENIS_CHOICES = [('Mobil', 'Mobil'), ('Motor', 'Motor')]
    STATUS_CHOICES = [('Tersedia', 'Tersedia'), ('Dirental', 'Dirental'), ('Perawatan', 'Perawatan')]
    TRANSMISI_CHOICES = [('Manual', 'Manual'), ('Otomatis', 'Otomatis')]

    plat_nomor = models.CharField(max_length=10, primary_key=True)
    merk = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    tahun = models.IntegerField()
    warna = models.CharField(max_length=20)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES)
    harga_sewa = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Tersedia')
    gambar = models.ImageField(upload_to='kendaraan/', blank=True, null=True)
    
    transmisi = models.CharField(max_length=10, choices=TRANSMISI_CHOICES, null=True, blank=True)
    jumlah_kursi = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"[{self.plat_nomor}] {self.merk} {self.model}"

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
    
    total_biaya = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=15, choices=STATUS_RESERVASI, default='Dipesan')
    created_at = models.DateTimeField(auto_now_add=True)

    def hitung_durasi(self):
        return (self.tgl_selesai - self.tgl_mulai).days

    def __str__(self):
        return f"Res #{self.id} - {self.pelanggan.username}"

class Tagihan(models.Model):
    STATUS_BAYAR = [('Belum Lunas', 'Belum Lunas'), ('Lunas', 'Lunas')]
    
    reservasi = models.OneToOneField(Reservasi, on_delete=models.CASCADE)
    
    total_denda = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_akhir = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=15, choices=STATUS_BAYAR, default='Belum Lunas')
    
    def __str__(self):
        return f"Invoice #{self.id} ({self.status})"
    
class Denda(models.Model):
    JENIS_DENDA = [('Keterlambatan', 'Keterlambatan'), ('Kerusakan', 'Kerusakan')]
    
    tagihan = models.ForeignKey(Tagihan, on_delete=models.CASCADE, related_name='daftar_denda')
    jenis = models.CharField(max_length=20, choices=JENIS_DENDA)
    jumlah = models.DecimalField(max_digits=12, decimal_places=0)
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return f"Denda: {self.jenis} - {self.jumlah}"

class Pembayaran(models.Model):
    METODE_BAYAR = [('Tunai', 'Tunai'), ('Transfer', 'Transfer')]

    tagihan = models.ForeignKey(Tagihan, on_delete=models.CASCADE, related_name='riwayat_pembayaran')
    jumlah = models.DecimalField(max_digits=12, decimal_places=0)
    tanggal = models.DateTimeField(default=timezone.now)
    metode = models.CharField(max_length=10, choices=METODE_BAYAR)
    
    diterima_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    bukti_transfer = models.ImageField(upload_to='bukti_bayar/', blank=True, null=True)
    
    def __str__(self):
        return f"Bayar: {self.jumlah} ({self.metode})"