from django.contrib import admin
from .models import ProfilPengguna, Kendaraan, Reservasi, Tagihan, Denda, Pembayaran

admin.site.register(ProfilPengguna)
admin.site.register(Kendaraan)
admin.site.register(Reservasi)
admin.site.register(Tagihan)
admin.site.register(Denda)
admin.site.register(Pembayaran)
