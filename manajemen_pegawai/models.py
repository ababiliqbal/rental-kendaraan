from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# ==========================================
# MANAJEMEN PEGAWAI MODELS (FITUR BARU)
# ==========================================

class Shift(models.Model):
    """Model untuk shift kerja pegawai"""
    NAMA_SHIFT_CHOICES = [
        ('Pagi', 'Pagi (06:00 - 14:00)'),
        ('Sore', 'Sore (14:00 - 22:00)'),
        ('Malam', 'Malam (22:00 - 06:00)'),
    ]
    
    nama_shift = models.CharField(max_length=20, choices=NAMA_SHIFT_CHOICES, unique=True)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    tunjangan_shift = models.PositiveIntegerField(default=0, help_text="Tunjangan tambahan per hari (Rupiah)")
    
    class Meta:
        verbose_name = "Shift"
        verbose_name_plural = "Daftar Shift"
        ordering = ['jam_mulai']
    
    def __str__(self):
        return f"{self.nama_shift} ({self.jam_mulai} - {self.jam_selesai})"


class Pegawai(models.Model):
    """Model untuk data pegawai"""
    STATUS_PEGAWAI_CHOICES = [
        ('Aktif', 'Aktif'),
        ('Cuti', 'Cuti'),
        ('Berhenti', 'Berhenti'),
        ('Non-Aktif', 'Non-Aktif'),
    ]
    
    JABATAN_CHOICES = [
        ('Manager', 'Manager'),
        ('Staff Admin', 'Staff Admin'),
        ('Staff Rental', 'Staff Rental'),
        ('Mekanik', 'Mekanik'),
        ('Driver', 'Driver'),
        ('Security', 'Security'),
    ]
    
    DEPARTEMEN_CHOICES = [
        ('Admin', 'Admin'),
        ('Rental', 'Rental'),
        ('Teknis', 'Teknis'),
        ('Keamanan', 'Keamanan'),
    ]
    
    # Relasi ke User Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pegawai_profile')
    
    # Identitas
    no_induk_pegawai = models.CharField(max_length=20, unique=True)
    no_ktp = models.CharField(max_length=20, unique=True)
    no_telepon = models.CharField(max_length=15)
    alamat = models.TextField()
    
    # Data Pekerjaan
    jabatan = models.CharField(max_length=50, choices=JABATAN_CHOICES)
    departemen = models.CharField(max_length=50, choices=DEPARTEMEN_CHOICES)
    tanggal_bergabung = models.DateField()
    gaji_pokok = models.PositiveIntegerField(help_text="Gaji pokok per bulan (Rupiah)")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_PEGAWAI_CHOICES, default='Aktif')
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    rating = models.FloatField(
        default=5.0, 
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Rating kinerja (1.0 - 5.0). Diinput manual oleh Admin."
    )
    
    # Jumlah Trip: Untuk keseimbangan beban kerja
    jumlah_trip = models.PositiveIntegerField(
        default=0, 
        help_text="Total perjalanan yang sudah ditugaskan."
    )
    
    @property
    def total_trip_sukses(self):
        # Kita perlu mengecek apakah relasi ini ada (untuk menghindari error pada pegawai non-driver)
        if hasattr(self, 'riwayat_menyetir'):
            return self.riwayat_menyetir.filter(status='Selesai').count()
        return 0
    
    class Meta:
        verbose_name = "Pegawai"
        verbose_name_plural = "Daftar Pegawai"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} (⭐{self.rating})"


class JadwalKerja(models.Model):
    """Model untuk jadwal/shift assignment"""
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='jadwal_kerja')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Jadwal Kerja"
        verbose_name_plural = "Jadwal Kerja Pegawai"
        ordering = ['-tanggal_mulai']
    
    def __str__(self):
        return f"{self.pegawai.user.get_full_name()} - {self.shift.nama_shift}"


class HistoriKerjaPegawai(models.Model):
    """Model untuk tracking absensi dan aktivitas pegawai"""
    TIPE_AKTIVITAS_CHOICES = [
        ('Masuk', 'Masuk'),
        ('Keluar', 'Keluar'),
        ('Izin', 'Izin'),
        ('Sakit', 'Sakit'),
        ('Cuti', 'Cuti'),
        ('Terlambat', 'Terlambat'),
        ('Tepat Waktu', 'Tepat Waktu'),
    ]
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='histori_kerja')
    tipe_aktivitas = models.CharField(max_length=20, choices=TIPE_AKTIVITAS_CHOICES)
    tanggal_waktu = models.DateTimeField(default=timezone.now)
    keterangan = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Histori Kerja"
        verbose_name_plural = "Histori Kerja Pegawai"
        ordering = ['-tanggal_waktu']
    
    def __str__(self):
        return f"{self.pegawai.user.get_full_name()} - {self.tipe_aktivitas} ({self.tanggal_waktu.date()})"


class GajiPegawai(models.Model):
    """Model untuk slip gaji pegawai"""
    STATUS_GAJI_CHOICES = [
        ('Belum Dibayar', 'Belum Dibayar'),
        ('Menunggu Verifikasi', 'Menunggu Verifikasi'),
        ('Sudah Dibayar', 'Sudah Dibayar'),
    ]
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='gaji_pegawai')
    bulan = models.DateField(help_text="Tanggal awal bulan gaji (contoh: 2024-12-01)")
    
    # Komponen Gaji
    gaji_pokok = models.PositiveIntegerField()
    tunjangan = models.PositiveIntegerField(default=0, help_text="Total tunjangan")
    potongan = models.PositiveIntegerField(default=0, help_text="Total potongan")
    
    # Total
    total_gaji = models.PositiveIntegerField()
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_GAJI_CHOICES, default='Belum Dibayar')
    tanggal_pembayaran = models.DateField(null=True, blank=True)
    dibayar_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gaji_yang_dibayarkan')
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Gaji Pegawai"
        verbose_name_plural = "Slip Gaji Pegawai"
        ordering = ['-bulan']
        unique_together = ['pegawai', 'bulan']
    
    def save(self, *args, **kwargs):
        """Auto-calculate total gaji"""
        self.total_gaji = self.gaji_pokok + self.tunjangan - self.potongan
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Gaji {self.pegawai.user.get_full_name()} - {self.bulan.strftime('%B %Y')}"


class Penghargaan(models.Model):
    """Model untuk bonus dan penghargaan pegawai"""
    TIPE_PENGHARGAAN_CHOICES = [
        ('Bonus', 'Bonus'),
        ('Insentif', 'Insentif'),
        ('THR', 'Tunjangan Hari Raya'),
        ('Penghargaan', 'Penghargaan Kinerja'),
        ('Lainnya', 'Lainnya'),
    ]
    
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE, related_name='penghargaan')
    tipe = models.CharField(max_length=50, choices=TIPE_PENGHARGAAN_CHOICES)
    nominal = models.PositiveIntegerField()
    tanggal = models.DateField(default=timezone.now)
    keterangan = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Penghargaan"
        verbose_name_plural = "Penghargaan Pegawai"
        ordering = ['-tanggal']
    
    def __str__(self):
        return f"{self.tipe} - {self.pegawai.user.get_full_name()} (Rp {self.nominal:,})"