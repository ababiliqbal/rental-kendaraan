from django.contrib import admin
# Tambahkan 'Kendaraan' ke dalam import
from .models import Kendaraan, KendaraanExt, Mobil, Motor, Garasi, Mitra

# Daftarkan Kendaraan agar muncul di menu Admin
admin.site.register(Mitra)
admin.site.register(Kendaraan) 
admin.site.register(KendaraanExt)
admin.site.register(Mobil)
admin.site.register(Motor)
admin.site.register(Garasi)