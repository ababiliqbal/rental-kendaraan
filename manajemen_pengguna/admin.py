from django.contrib import admin
# Import model-model yang sudah kita buat
from .models import ProfilPengguna, Reservasi, Tagihan, Pembayaran

# Daftarkan model agar muncul di Admin Panel
admin.site.register(ProfilPengguna)
admin.site.register(Reservasi)
admin.site.register(Tagihan)
admin.site.register(Pembayaran)