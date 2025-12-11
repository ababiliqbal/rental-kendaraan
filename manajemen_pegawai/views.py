import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User 

from manajemen_pengguna.models import Reservasi, Tagihan, Denda
from kendaraan_ext.models import Kendaraan, Mitra
from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan

from .forms import (
    FormPengembalian, KendaraanForm, MobilForm, MotorForm, MitraForm,
    PegawaiForm, ShiftForm, JadwalKerjaForm, HistoriKerjaPegawaiForm, 
    GajiPegawaiForm, PenghargaanForm
)

def cek_pegawai(user):
    return user.is_authenticated and (user.is_superuser or user.profil.is_pegawai)

@user_passes_test(cek_pegawai, login_url='home')
def dashboard_pegawai(request):
    tagihan_pending = Tagihan.objects.filter(status='Menunggu Verifikasi').order_by('id')
    
    tabel_reservasi = Reservasi.objects.filter(status__in=['Dipesan', 'Aktif']).order_by('-tgl_mulai')
    
    real_sewa_aktif = Reservasi.objects.filter(status='Aktif').count()
    
    context = {
        'tagihan_pending': tagihan_pending,
        'reservasi_aktif': tabel_reservasi,
        
        'total_pending': tagihan_pending.count(),
        

        'total_aktif': real_sewa_aktif 
    }
    return render(request, 'manajemen_pegawai/dashboard.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def verifikasi_pembayaran(request, tagihan_id, aksi):
    tagihan = get_object_or_404(Tagihan, id=tagihan_id)
    
    if aksi == 'terima':
        tagihan.status = 'Lunas'
        tagihan.save()
        messages.success(request, f"Pembayaran Order #{tagihan.reservasi.id} DITERIMA!")

    elif aksi == 'tolak':
        tagihan.status = 'Belum Lunas'
        tagihan.save()
        
        pembayaran_terakhir = tagihan.riwayat_pembayaran.last()
        if pembayaran_terakhir:
            pembayaran_terakhir.is_valid = False
            pembayaran_terakhir.save()

        messages.warning(request, f"Pembayaran Order #{tagihan.reservasi.id} DITOLAK. User diminta upload ulang.")
        
    return redirect('dashboard_pegawai')


@user_passes_test(cek_pegawai, login_url='home')
def proses_pengembalian(request, reservasi_id):
    reservasi = get_object_or_404(Reservasi, id=reservasi_id)
    tagihan = reservasi.tagihan # Ambil tagihan terkait
    
    # Hitung Keterlambatan Otomatis
    today = timezone.now().date()
    tgl_selesai = reservasi.tgl_selesai
    
    telat_hari = 0
    denda_telat = 0
    
    if today > tgl_selesai:
        telat_hari = (today - tgl_selesai).days
        # Rumus: Denda Telat = Hari Telat x Harga Sewa Per Hari
        denda_telat = telat_hari * reservasi.kendaraan.harga_sewa_per_hari

    if request.method == 'POST':
        form = FormPengembalian(request.POST)
        if form.is_valid():
            # 1. Simpan Denda Keterlambatan (Kalau ada)
            if denda_telat > 0:
                Denda.objects.create(
                    tagihan=tagihan,
                    jenis="Keterlambatan",
                    jumlah=denda_telat,
                    keterangan=f"Telat {telat_hari} hari (x Rp {reservasi.kendaraan.harga_sewa_per_hari})"
                )

            # 2. Simpan Denda Kerusakan (Dari Form)
            biaya_rusak = form.cleaned_data['denda_kerusakan']
            ket_rusak = form.cleaned_data['keterangan_kerusakan']
            
            if biaya_rusak > 0:
                Denda.objects.create(
                    tagihan=tagihan,
                    jenis="Kerusakan Fisik",
                    jumlah=biaya_rusak,
                    keterangan=ket_rusak
                )
            
            # 3. Update Total Tagihan
            total_denda = denda_telat + biaya_rusak
            if total_denda > 0:
                tagihan.total_denda = total_denda
                tagihan.total_akhir += total_denda
                tagihan.status = 'Belum Lunas' # Ubah jadi Belum Lunas biar user bayar dendanya
                tagihan.save()
                messages.warning(request, f"Pengembalian tercatat dengan total denda Rp {total_denda:,}. Tagihan diperbarui.")
            else:
                messages.success(request, "Mobil dikembalikan tepat waktu & tanpa kerusakan. Sewa Selesai.")

            # 4. Update Status Reservasi & Mobil
            reservasi.status = 'Selesai'
            reservasi.tgl_pengembalian_aktual = today
            reservasi.save()
            
            reservasi.kendaraan.status = 'Tersedia'
            reservasi.kendaraan.save()
            
            return redirect('dashboard_pegawai')

    else:
        form = FormPengembalian()

    context = {
        'reservasi': reservasi,
        'form': form,
        'telat_hari': telat_hari,
        'denda_telat': denda_telat,
    }
    return render(request, 'manajemen_pegawai/form_pengembalian.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def update_status_pesanan(request, reservasi_id, status_baru):
    reservasi = get_object_or_404(Reservasi, id=reservasi_id)
    kendaraan = reservasi.kendaraan
    
    if status_baru == 'aktif':
        # Mobil Diambil Pelanggan
        reservasi.status = 'Aktif'
        reservasi.save()
        
        # Update Status Kendaraan jadi "Dirental"
        kendaraan.status = 'Dirental'
        kendaraan.save()
        messages.info(request, "Mobil telah diserahterimakan (Sewa Dimulai).")
        
    elif status_baru == 'selesai':
        # Mobil Dikembalikan
        reservasi.status = 'Selesai'
        reservasi.tgl_pengembalian_aktual = timezone.now().date()
        reservasi.save()
        
        # Update Status Kendaraan jadi "Tersedia" lagi
        kendaraan.status = 'Tersedia'
        kendaraan.save()
        messages.success(request, "Mobil telah dikembalikan (Sewa Selesai).")

    return redirect('dashboard_pegawai')

# ==========================================
# MANAJEMEN ARMADA (CRUD)
# ==========================================

@user_passes_test(cek_pegawai, login_url='home')
def daftar_armada(request):
    # Ambil semua kendaraan, urutkan dari yang terbaru
    armada = Kendaraan.objects.all().order_by('-id')
    return render(request, 'manajemen_pegawai/daftar_armada.html', {'armada': armada})

@user_passes_test(cek_pegawai, login_url='home')
def tambah_mobil(request):
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES)
        m_form = MobilForm(request.POST)
        
        if k_form.is_valid() and m_form.is_valid():
            try:
                with transaction.atomic(): # Transaksi Database Aman
                    # 1. Simpan Kendaraan (Induk)
                    kendaraan = k_form.save()
                    
                    # 2. Simpan Mobil (Anak) & Hubungkan
                    mobil = m_form.save(commit=False)
                    mobil.kendaraan = kendaraan # Link OneToOne
                    mobil.save()
                    
                messages.success(request, f"Mobil {kendaraan.merk} {kendaraan.model} berhasil ditambahkan!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {e}")
    else:
        k_form = KendaraanForm()
        m_form = MobilForm()

    context = {
        'k_form': k_form, 
        'm_form': m_form, 
        'title': 'Tambah Mobil Baru',
        'icon': 'fa-car'
    }
    return render(request, 'manajemen_pegawai/form_armada.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def tambah_motor(request):
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES)
        m_form = MotorForm(request.POST)
        
        if k_form.is_valid() and m_form.is_valid():
            try:
                with transaction.atomic():
                    kendaraan = k_form.save()
                    motor = m_form.save(commit=False)
                    motor.kendaraan = kendaraan
                    motor.save()
                    
                messages.success(request, f"Motor {kendaraan.merk} {kendaraan.model} berhasil ditambahkan!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Gagal menyimpan: {e}")
    else:
        k_form = KendaraanForm()
        m_form = MotorForm()

    context = {
        'k_form': k_form, 
        'm_form': m_form, 
        'title': 'Tambah Motor Baru',
        'icon': 'fa-motorcycle'
    }
    # Kita pakai template yang sama (Reusable Template)
    return render(request, 'manajemen_pegawai/form_armada.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def hapus_kendaraan(request, pk):
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    if request.method == 'POST':
        kendaraan.delete()
        messages.success(request, "Data kendaraan berhasil dihapus.")
        return redirect('daftar_armada')

# manajemen_pegawai/views.py

@user_passes_test(cek_pegawai, login_url='home')
def edit_armada(request, pk):
    # 1. Ambil data kendaraan induk
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    
    # 2. Deteksi Jenis & Siapkan Variable
    child_instance = None
    ChildForm = None
    jenis_str = ""
    icon = ""

    if hasattr(kendaraan, 'detail_mobil'):
        child_instance = kendaraan.detail_mobil
        ChildForm = MobilForm
        jenis_str = "Mobil"
        icon = "fa-car"
    elif hasattr(kendaraan, 'detail_motor'):
        child_instance = kendaraan.detail_motor
        ChildForm = MotorForm
        jenis_str = "Motor"
        icon = "fa-motorcycle"
    
    if ChildForm is None:
        messages.error(request, f"Data kendaraan '{kendaraan.plat_nomor}' tidak valid atau tidak lengkap (Hanya data induk). Silakan hapus dan buat ulang.")
        return redirect('daftar_armada')
    
    # 3. Proses Form
    if request.method == 'POST':
        k_form = KendaraanForm(request.POST, request.FILES, instance=kendaraan)
        # Load form anak dengan instance yang sesuai
        c_form = ChildForm(request.POST, instance=child_instance)
        
        if k_form.is_valid() and c_form.is_valid():
            try:
                with transaction.atomic():
                    k_form.save()
                    c_form.save()
                messages.success(request, f"Data {jenis_str} {kendaraan.merk} berhasil diperbarui!")
                return redirect('daftar_armada')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        # GET: Isi form dengan data yang sudah ada
        k_form = KendaraanForm(instance=kendaraan)
        c_form = ChildForm(instance=child_instance)

    context = {
        'k_form': k_form,
        'm_form': c_form, # Kita pakai nama variabel yang sama dgn 'tambah' biar template reusable
        'title': f'Edit Data {jenis_str}',
        'icon': icon,
        'is_edit': True # Flag untuk membedakan tampilan tombol
    }
    
    # Kita gunakan template yang sama dengan Tambah Armada
    return render(request, 'manajemen_pegawai/form_armada.html', context)

# ==========================================
# MANAJEMEN MITRA
# ==========================================

@user_passes_test(cek_pegawai, login_url='home')
def daftar_mitra(request):
    mitra_list = Mitra.objects.all().order_by('nama')
    return render(request, 'manajemen_pegawai/daftar_mitra.html', {'mitra_list': mitra_list})

@user_passes_test(cek_pegawai, login_url='home')
def tambah_mitra(request):
    if request.method == 'POST':
        form = MitraForm(request.POST)
        if form.is_valid():
            mitra = form.save()
            messages.success(request, f"Mitra '{mitra.nama}' berhasil ditambahkan!")
            return redirect('daftar_mitra')
    else:
        form = MitraForm()
    
    context = {'form': form, 'title': 'Tambah Mitra Baru', 'icon': 'fa-handshake'}
    return render(request, 'manajemen_pegawai/form_mitra.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def edit_mitra(request, pk):
    mitra = get_object_or_404(Mitra, pk=pk)
    if request.method == 'POST':
        form = MitraForm(request.POST, instance=mitra)
        if form.is_valid():
            form.save()
            messages.success(request, f"Data Mitra '{mitra.nama}' berhasil diperbarui!")
            return redirect('daftar_mitra')
    else:
        form = MitraForm(instance=mitra)
    
    context = {'form': form, 'title': 'Edit Data Mitra', 'icon': 'fa-edit'}
    return render(request, 'manajemen_pegawai/form_mitra.html', context)

@user_passes_test(cek_pegawai, login_url='home')
def hapus_mitra(request, pk):
    mitra = get_object_or_404(Mitra, pk=pk)
    if request.method == 'POST':
        nama = mitra.nama
        mitra.delete()
        messages.success(request, f"Mitra '{nama}' telah dihapus.")
        return redirect('daftar_mitra')
    
class PegawaiListView(LoginRequiredMixin, ListView):
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_list.html'
    context_object_name = 'pegawai_list'
    paginate_by = 10

class PegawaiDetailView(LoginRequiredMixin, DetailView):
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_detail.html'
    context_object_name = 'pegawai'

class PegawaiCreateView(LoginRequiredMixin, CreateView):
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'manajemen_pegawai/pegawai_form.html'
    success_url = reverse_lazy('pegawai_list')

    def form_valid(self, form):
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")

        if not email:
             messages.error(self.request, 'Email wajib diisi untuk membuat akun.')
             return self.form_invalid(form)

        username = email.split("@")[0]
        # Auto-create User Django
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="pegawai123" 
        )
        form.instance.user = user
        messages.success(self.request, 'Pegawai baru berhasil ditambahkan!')
        return super().form_valid(form)

class PegawaiUpdateView(LoginRequiredMixin, UpdateView):
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'manajemen_pegawai/pegawai_form.html'
    success_url = reverse_lazy('pegawai_list')
    
    def get_initial(self):
        initial = super().get_initial()
        if self.object.user:
            initial['first_name'] = self.object.user.first_name
            initial['last_name'] = self.object.user.last_name
            initial['email'] = self.object.user.email
        return initial
    
    def form_valid(self, form):
        user = self.object.user
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save()
        messages.success(self.request, 'Data pegawai berhasil diperbarui!')
        return super().form_valid(form)

class PegawaiDeleteView(LoginRequiredMixin, DeleteView):
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_confirm_delete.html'
    success_url = reverse_lazy('pegawai_list')

    def delete(self, request, *args, **kwargs):
        pegawai_obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Pegawai {pegawai_obj.user.get_full_name()} berhasil dihapus!')
        return response

# --- SHIFT ---
class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = 'manajemen_pegawai/shift_list.html'
    context_object_name = 'daftar_shift'

class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    form_class = ShiftForm
    template_name = 'manajemen_pegawai/shift_form.html'
    success_url = reverse_lazy('shift_list')

    def form_valid(self, form):
        messages.success(self.request, "Shift baru berhasil ditambahkan!")
        return super().form_valid(form)

class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    form_class = ShiftForm
    template_name = 'manajemen_pegawai/shift_form.html'
    success_url = reverse_lazy('shift_list')

    def form_valid(self, form):
        messages.success(self.request, f"Shift '{self.object.get_nama_shift_display()}' berhasil diperbarui!")
        return super().form_valid(form)

class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = 'manajemen_pegawai/shift_detail.html'
    context_object_name = 'shift'

class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = 'manajemen_pegawai/shift_confirm_delete.html'
    success_url = reverse_lazy('shift_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object() 
        shift_nama = obj.get_nama_shift_display()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Shift '{shift_nama}' berhasil dihapus!")
        return response

# --- JADWAL KERJA ---
class JadwalKerjaListView(LoginRequiredMixin, ListView):
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_list.html'
    context_object_name = 'jadwal_list'
    ordering = ['-tanggal_mulai']

class JadwalKerjaCreateView(LoginRequiredMixin, CreateView):
    model = JadwalKerja
    form_class = JadwalKerjaForm
    template_name = 'manajemen_pegawai/jadwal_form.html'
    success_url = reverse_lazy('jadwal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil ditambahkan!")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"Gagal membuat jadwal: {error}")
                else:
                    field_name = form.fields.get(field).label or field.capitalize()
                    messages.error(self.request, f"Gagal membuat jadwal ({field_name}): {error}")
        return super().form_invalid(form)

class JadwalKerjaDetailView(LoginRequiredMixin, DetailView):
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_detail.html'
    context_object_name = 'jadwal'

class JadwalKerjaUpdateView(LoginRequiredMixin, UpdateView):
    model = JadwalKerja
    form_class = JadwalKerjaForm
    template_name = 'manajemen_pegawai/jadwal_form.html'
    success_url = reverse_lazy('jadwal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil diperbarui!")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"Gagal memperbarui jadwal: {error}")
                else:
                    field_name = form.fields.get(field).label or field.capitalize()
                    messages.error(self.request, f"Gagal memperbarui jadwal ({field_name}): {error}")
        return super().form_invalid(form)

class JadwalKerjaDeleteView(LoginRequiredMixin, DeleteView):
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_confirm_delete.html'
    success_url = reverse_lazy('jadwal_list')
    context_object_name = 'jadwal'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil dihapus!")
        return response

# --- GAJI ---
class GajiPegawaiListView(LoginRequiredMixin, ListView):
    model = GajiPegawai
    template_name = 'manajemen_pegawai/gaji_list.html'
    context_object_name = 'gaji_list'
    paginate_by = 10
    ordering = ['-bulan']

class GajiPegawaiCreateView(LoginRequiredMixin, CreateView):
    model = GajiPegawai
    form_class = GajiPegawaiForm
    template_name = 'manajemen_pegawai/gaji_form.html'
    success_url = reverse_lazy('gaji_list')

    def form_valid(self, form):
        messages.success(self.request, "Slip gaji berhasil dibuat!")
        return super().form_valid(form)

class GajiPegawaiUpdateView(LoginRequiredMixin, UpdateView):
    model = GajiPegawai
    form_class = GajiPegawaiForm
    template_name = 'manajemen_pegawai/gaji_form.html'
    success_url = reverse_lazy('gaji_list')

    def form_valid(self, form):
        messages.success(self.request, "Slip gaji berhasil diperbarui!")
        return super().form_valid(form)

class GajiPegawaiDetailView(LoginRequiredMixin, DetailView):
    model = GajiPegawai
    template_name = 'manajemen_pegawai/gaji_detail.html'
    context_object_name = 'gaji'