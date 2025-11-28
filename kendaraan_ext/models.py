from django.db import models
from rental_app.models import Kendaraan   # ← Import model temanmu


class KendaraanExt(models.Model):
    KEPEMILIKAN_CHOICES = [
        ("Milik Sendiri", "Milik Sendiri"),
        ("Mitra", "Mitra"),
    ]

    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE)

    tipe_kepemilikan = models.CharField(
        max_length=20,
        choices=KEPEMILIKAN_CHOICES,
        default="Milik Sendiri"
    )
    id_mitra = models.CharField(max_length=50, null=True, blank=True)
    persen_bagi_hasil = models.FloatField(default=0.0)

    def __str__(self):
        prefix = "[MITRA] " if self.tipe_kepemilikan == "Mitra" else ""
        return f"{prefix}{self.kendaraan}"


class Mobil(models.Model):
    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE)
    jumlah_kursi = models.PositiveIntegerField()
    transmisi = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.kendaraan} | Kursi: {self.jumlah_kursi} | Transmisi: {self.transmisi}"


class Motor(models.Model):
    kendaraan = models.OneToOneField(Kendaraan, on_delete=models.CASCADE)
    tipe_motor = models.CharField(max_length=30)
    kapasitas_mesin_cc = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.kendaraan} | Tipe: {self.tipe_motor} | CC: {self.kapasitas_mesin_cc}"


class Garasi(models.Model):
    lokasi = models.CharField(max_length=100)
    kendaraan = models.ManyToManyField(Kendaraan)

    def __str__(self):
        return self.lokasi

    def jumlah_kendaraan(self):
        return self.kendaraan.count()
