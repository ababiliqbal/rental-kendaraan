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


# ==========================================
# PEGAWAI VIEWS
# ==========================================

class PegawaiListView(LoginRequiredMixin, ListView):
    """List semua pegawai"""
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_list.html'
    context_object_name = 'pegawai_list'
    paginate_by = 10


class PegawaiDetailView(LoginRequiredMixin, DetailView):
    """Detail pegawai"""
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_detail.html'
    context_object_name = 'pegawai'


class PegawaiCreateView(LoginRequiredMixin, CreateView):
    """Create pegawai baru"""
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'manajemen_pegawai/pegawai_form.html'
    success_url = reverse_lazy('pegawai_list')
    
    def form_valid(self, form):
        """
        Override: buat User baru berdasarkan form, lalu set ke Pegawai.user.
        """
        # 1. Ambil data user dari form
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")

        # 2. Buat user baru
        username = email.split("@")[0]  # contoh otomatis
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="pegawai123"   # default, bisa diganti
        )

        # 3. Set ke pegawai
        form.instance.user = user

        messages.success(self.request, 'Pegawai berhasil ditambahkan!')
        return super().form_valid(form)



class PegawaiUpdateView(LoginRequiredMixin, UpdateView):
    """Update data pegawai"""
    model = Pegawai
    form_class = PegawaiForm
    template_name = 'manajemen_pegawai/pegawai_form.html'
    success_url = reverse_lazy('pegawai_list')
    
    def get_initial(self):
        """Pre-fill form dengan data User"""
        initial = super().get_initial()

        if self.object.user:  # aman dari error
            initial['first_name'] = self.object.user.first_name
            initial['last_name'] = self.object.user.last_name
            initial['email'] = self.object.user.email

        return initial
    
    def form_valid(self, form):
        """
        Update user juga.
        """
        user = self.object.user

        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save()

        messages.success(self.request, 'Data pegawai berhasil diupdate!')
        return super().form_valid(form)



class PegawaiDeleteView(LoginRequiredMixin, DeleteView):
    """Delete pegawai"""
    model = Pegawai
    template_name = 'manajemen_pegawai/pegawai_confirm_delete.html'
    success_url = reverse_lazy('pegawai_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Pegawai berhasil dihapus!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# SHIFT VIEWS
# ==========================================

class ShiftListView(LoginRequiredMixin, ListView):
    """List semua shift"""
    model = Shift
    template_name = 'manajemen_pegawai/shift_list.html'
    context_object_name = 'shift_list'


class ShiftCreateView(LoginRequiredMixin, CreateView):
    """Create shift baru"""
    model = Shift
    form_class = ShiftForm
    template_name = 'manajemen_pegawai/shift_form.html'
    success_url = reverse_lazy('shift_list')


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    """Update shift"""
    model = Shift
    form_class = ShiftForm
    template_name = 'manajemen_pegawai/shift_form.html'
    success_url = reverse_lazy('shift_list')


# ==========================================
# GAJI PEGAWAI VIEWS
# ==========================================

class GajiPegawaiListView(LoginRequiredMixin, ListView):
    """List semua slip gaji"""
    model = GajiPegawai
    template_name = 'manajemen_pegawai/gaji_list.html'
    context_object_name = 'gaji_list'
    paginate_by = 10
    ordering = ['-bulan']


class GajiPegawaiCreateView(LoginRequiredMixin, CreateView):
    """Create slip gaji baru"""
    model = GajiPegawai
    form_class = GajiPegawaiForm
    template_name = 'manajemen_pegawai/gaji_form.html'
    success_url = reverse_lazy('gaji_list')


class GajiPegawaiUpdateView(LoginRequiredMixin, UpdateView):
    """Update slip gaji"""
    model = GajiPegawai
    form_class = GajiPegawaiForm
    template_name = 'manajemen_pegawai/gaji_form.html'
    success_url = reverse_lazy('gaji_list')


# ==========================================
# JADWAL KERJA VIEWS
# ==========================================

class JadwalKerjaListView(LoginRequiredMixin, ListView):
    """List jadwal kerja"""
    model = JadwalKerja
    template_name = 'manajemen_pegawai/jadwal_list.html'
    context_object_name = 'jadwal_list'
    ordering = ['-tanggal_mulai']


class JadwalKerjaCreateView(LoginRequiredMixin, CreateView):
    """Create jadwal kerja"""
    model = JadwalKerja
    form_class = JadwalKerjaForm
    template_name = 'manajemen_pegawai/jadwal_form.html'
    success_url = reverse_lazy('jadwal_list')