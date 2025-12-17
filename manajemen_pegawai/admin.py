from django.contrib import admin
# Import model dari aplikasi manajemen_pegawai
from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan

# ==========================================
# 1. PEGAWAI ADMIN (CUSTOM)
# ==========================================
class PegawaiAdmin(admin.ModelAdmin):
    # Kolom yang akan muncul di tabel daftar pegawai
    list_display = ('get_nama_lengkap', 'jabatan', 'status', 'rating', 'jumlah_trip') 
    
    # Filter samping (sidebar)
    list_filter = ('jabatan', 'status', 'departemen')
    
    # Kotak pencarian (bisa cari nama atau user)
    search_fields = ('user__username', 'user__first_name', 'no_induk_pegawai')
    
    # [FITUR KEREN] Edit Rating & Status langsung dari tabel luar (Quick Edit)
    list_editable = ('rating', 'status') 
    
    # Menampilkan nama lengkap agar lebih rapi di tabel
    def get_nama_lengkap(self, obj):
        return obj.user.get_full_name()
    get_nama_lengkap.short_description = 'Nama Pegawai'

# ==========================================
# 2. REGISTER MODEL LAINNYA
# ==========================================
# Daftarkan model lain agar muncul juga di admin panel
admin.site.register(Pegawai, PegawaiAdmin)
admin.site.register(Shift)
admin.site.register(JadwalKerja)
admin.site.register(HistoriKerjaPegawai)
admin.site.register(GajiPegawai)
admin.site.register(Penghargaan)