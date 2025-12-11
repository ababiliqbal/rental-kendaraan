from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Pegawai, Shift, JadwalKerja, HistoriKerjaPegawai, GajiPegawai, Penghargaan
from .forms import (
    PegawaiForm, ShiftForm, JadwalKerjaForm, 
    HistoriKerjaPegawaiForm, GajiPegawaiForm, PenghargaanForm
)

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
        # 1. Ambil data User dari Form (yang harus ada di PegawaiForm)
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")

        # 2. Logika pembuatan username (Jika email tidak ada, username tidak bisa dibuat)
        if not email:
             # Tambahkan penanganan error jika email tidak ada
             messages.error(self.request, 'Email wajib diisi untuk membuat akun.')
             return self.form_invalid(form)

        username = email.split("@")[0]
        
        # 3. Buat objek User baru
        # Catatan: Password diset statis "pegawai123"
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="pegawai123" 
        )

        # 4. Hubungkan objek Pegawai (form.instance) dengan User yang baru dibuat
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
        # Mengisi nilai awal Form dengan data dari objek User yang terkait
        if self.object.user:
            initial['first_name'] = self.object.user.first_name
            initial['last_name'] = self.object.user.last_name
            initial['email'] = self.object.user.email
        return initial
    
    def form_valid(self, form):
        # 1. Update data pada Model User yang sudah ada
        user = self.object.user
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save() # Simpan perubahan ke Model User

        # 2. Lanjutkan dengan menyimpan data Pegawai
        messages.success(self.request, 'Data pegawai berhasil diperbarui!')
        return super().form_valid(form) # Menyimpan perubahan ke Model Pegawai


class PegawaiDeleteView(LoginRequiredMixin, DeleteView):
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_confirm_delete.html'
    success_url = reverse_lazy('pegawai_list')

    def delete(self, request, *args, **kwargs):
        """Menghapus objek Pegawai dan User yang terkait."""
        pegawai_obj = self.get_object()
        
        # Karena models.OneToOneField(User, on_delete=models.CASCADE)
        # Menghapus objek Pegawai akan otomatis menghapus objek User.
        # Namun, kita bisa menambahkan konfirmasi pesan sebelum penghapusan terjadi.
        
        # Hapus objek Pegawai. User akan ikut terhapus (CASCADE).
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Pegawai {pegawai_obj.user.get_full_name()} berhasil dihapus!')
        return response


# ==========================================
# SHIFT VIEWS
# ==========================================

class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = 'manajemen_pegawai/shift_list.html'
    context_object_name = 'daftar_shift' # <--- PERBAIKAN: Menggunakan nama konteks yang konsisten

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
        # Menggunakan self.object.get_nama_shift_display() untuk pesan yang lebih informatif
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
        # Menggunakan self.get_object() sebelum dihapus untuk mendapatkan nama
        obj = self.get_object() 
        shift_nama = obj.get_nama_shift_display()
        
        # Panggil method delete dari superclass
        response = super().delete(request, *args, **kwargs)
        
        messages.success(request, f"Shift '{shift_nama}' berhasil dihapus!")
        return response

# =======================================================================
# JADWAL KERJA
# =======================================================================

class JadwalKerjaListView(LoginRequiredMixin, ListView):
    """Menampilkan daftar semua jadwal kerja."""
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_list.html'
    context_object_name = 'jadwal_list'
    ordering = ['-tanggal_mulai']


class JadwalKerjaCreateView(LoginRequiredMixin, CreateView):
    """Menangani pembuatan jadwal kerja baru."""
    model = JadwalKerja
    form_class = JadwalKerjaForm  # Menggunakan form yang sudah memiliki validasi overlap
    template_name = 'manajemen_pegawai/jadwal_form.html'
    success_url = reverse_lazy('jadwal_list')

    def form_valid(self, form):
        """
        Dipanggil ketika data form valid.
        Validasi bisnis (overlap) sudah dilakukan di forms.py.
        """
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil ditambahkan!")
        return response

    def form_invalid(self, form):
        """
        Dipanggil ketika data form tidak valid.
        Menampilkan pesan kesalahan yang berasal dari form, seperti validasi overlap.
        """
        # Iterasi melalui semua error field (termasuk error non-field)
        for field, errors in form.errors.items():
            for error in errors:
                # Tampilkan pesan error kepada user
                if field == '__all__':
                    # Ini biasanya untuk error non-field seperti error overlap dari clean()
                    messages.error(self.request, f"Gagal membuat jadwal: {error}")
                else:
                    # Error untuk field spesifik
                    # Menggunakan .get(field).label untuk mendapatkan label yang lebih user-friendly
                    field_name = form.fields.get(field).label or field.capitalize()
                    messages.error(self.request, f"Gagal membuat jadwal ({field_name}): {error}")
                
        # Selalu kembalikan response form_invalid untuk me-render ulang form dengan error
        return super().form_invalid(form)


class JadwalKerjaDetailView(LoginRequiredMixin, DetailView):
    """Menampilkan detail spesifik dari sebuah jadwal kerja."""
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_detail.html'
    context_object_name = 'jadwal'


class JadwalKerjaUpdateView(LoginRequiredMixin, UpdateView):
    """Menangani pembaruan (update) jadwal kerja yang sudah ada."""
    model = JadwalKerja
    form_class = JadwalKerjaForm  # Menggunakan form yang sama dengan CreateView
    template_name = 'manajemen_pegawai/jadwal_form.html'
    success_url = reverse_lazy('jadwal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil diperbarui!")
        return response

    def form_invalid(self, form):
        # Implementasi error handling yang sama seperti di CreateView
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"Gagal memperbarui jadwal: {error}")
                else:
                    field_name = form.fields.get(field).label or field.capitalize()
                    messages.error(self.request, f"Gagal memperbarui jadwal ({field_name}): {error}")
                
        return super().form_invalid(form)


class JadwalKerjaDeleteView(LoginRequiredMixin, DeleteView):
    """Menangani penghapusan jadwal kerja."""
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_confirm_delete.html'
    success_url = reverse_lazy('jadwal_list')
    context_object_name = 'jadwal'

    def form_valid(self, form):
        """Tambahkan pesan sukses setelah penghapusan."""
        response = super().form_valid(form)
        messages.success(self.request, "Jadwal kerja berhasil dihapus!")
        return response
    
# =======================================================================
# GAJI
# =======================================================================

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


# =======================================================================
# HISTORI KERJA (Opsional)
# =======================================================================

class HistoriKerjaCreateView(LoginRequiredMixin, CreateView):
    model = HistoriKerjaPegawai
    form_class = HistoriKerjaPegawaiForm
    template_name = 'manajemen_pegawai/histori_form.html'
    success_url = reverse_lazy('pegawai_list')

    def form_valid(self, form):
        messages.success(self.request, "Histori kerja pegawai berhasil ditambahkan!")
        return super().form_valid(form)


# =======================================================================
# PENGHARGAAN
# =======================================================================

class PenghargaanCreateView(LoginRequiredMixin, CreateView):
    model = Penghargaan
    form_class = PenghargaanForm
    template_name = 'manajemen_pegawai/penghargaan_form.html'
    success_url = reverse_lazy('pegawai_list')

    def form_valid(self, form):
        messages.success(self.request, "Penghargaan berhasil diberikan kepada pegawai!")
        return super().form_valid(form)
