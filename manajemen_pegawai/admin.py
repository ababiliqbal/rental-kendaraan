from django.contrib import admin
from .models import Shift, Pegawai, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['nama_shift', 'jam_mulai', 'jam_selesai', 'tunjangan_shift']
    search_fields = ['nama_shift']
    list_filter = ['nama_shift']


@admin.register(Pegawai)
class PegawaiAdmin(admin.ModelAdmin):
    list_display = ['no_induk_pegawai', 'user', 'jabatan', 'departemen', 'status', 'created_at']
    search_fields = ['no_induk_pegawai', 'user__first_name', 'user__last_name', 'no_ktp']
    list_filter = ['status', 'jabatan', 'departemen', 'created_at']
    fieldsets = (
        ('Data User', {'fields': ('user',)}),
        ('Data Identitas', {'fields': ('no_induk_pegawai', 'no_ktp', 'no_telepon', 'alamat')}),
        ('Data Pekerjaan', {'fields': ('jabatan', 'departemen', 'tanggal_bergabung', 'gaji_pokok')}),
        ('Status', {'fields': ('status',)}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JadwalKerja)
class JadwalKerjaAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'shift', 'tanggal_mulai', 'tanggal_selesai']
    search_fields = ['pegawai__user__first_name', 'pegawai__user__last_name']
    list_filter = ['shift', 'tanggal_mulai']


@admin.register(HistoriKerjaPegawai)
class HistoriKerjaPegawaiAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'tipe_aktivitas', 'tanggal_waktu', 'keterangan']
    search_fields = ['pegawai__user__first_name', 'pegawai__user__last_name']
    list_filter = ['tipe_aktivitas', 'tanggal_waktu']
    readonly_fields = ['tanggal_waktu']


@admin.register(GajiPegawai)
class GajiPegawaiAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'bulan', 'gaji_pokok', 'total_gaji', 'status']
    search_fields = ['pegawai__user__first_name', 'pegawai__user__last_name']
    list_filter = ['status', 'bulan']
    fieldsets = (
        ('Data Pegawai', {'fields': ('pegawai', 'bulan')}),
        ('Komponen Gaji', {'fields': ('gaji_pokok', 'tunjangan', 'potongan', 'total_gaji')}),
        ('Pembayaran', {'fields': ('status', 'tanggal_pembayaran', 'dibayar_oleh')}),
    )
    readonly_fields = ['total_gaji', 'created_at', 'updated_at']


@admin.register(Penghargaan)
class PenghargaanAdmin(admin.ModelAdmin):
    list_display = ['pegawai', 'tipe', 'nominal', 'tanggal']
    search_fields = ['pegawai__user__first_name', 'pegawai__user__last_name']
    list_filter = ['tipe', 'tanggal']