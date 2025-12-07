# kendaraan/views.py (BAGIAN YANG BERUBAH)

from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, DeleteView
)
from .models import Kendaraan, Mobil, Motor, Garasi
from .forms import KendaraanForm, MobilForm, MotorForm, GarasiForm
from django.db import transaction

# READ (Daftar Kendaraan)
class DaftarKendaraanView(ListView):
    model = Kendaraan
    # --- PERUBAHAN NAMA TEMPLATE ---
    template_name = 'kendaraan/kendaraan_list.html' 
    context_object_name = 'daftar_kendaraan'

# READ (Detail Kendaraan)
class DetailKendaraanView(DetailView):
    model = Kendaraan
    # --- PERUBAHAN NAMA TEMPLATE ---
    template_name = 'kendaraan/kendaraan_detail.html' 
    context_object_name = 'kendaraan'


# CREATE (Tambah Kendaraan + Detail Mobil/Motor) - FUNCTION BASED VIEW
def tambah_kendaraan(request):
    kendaraan_form = KendaraanForm(request.POST or None, request.FILES or None)
    mobil_form = MobilForm(request.POST or None)
    motor_form = MotorForm(request.POST or None)
    
    # ... (Logika POST dan Form Validation yang sama seperti sebelumnya) ...
    if request.method == 'POST':
        tipe_kendaraan = request.POST.get('tipe_kendaraan')
        if kendaraan_form.is_valid():
            with transaction.atomic():
                kendaraan = kendaraan_form.save()
                detail_saved = False
                # ... (Logika penyimpanan Mobil/Motor) ...

                if tipe_kendaraan == 'Mobil' and mobil_form.is_valid():
                    Mobil.objects.create(kendaraan=kendaraan, **mobil_form.cleaned_data)
                    detail_saved = True
                
                elif tipe_kendaraan == 'Motor' and motor_form.is_valid():
                    Motor.objects.create(kendaraan=kendaraan, **motor_form.cleaned_data)
                    detail_saved = True
                
                elif not tipe_kendaraan:
                    detail_saved = True 
                
                if not detail_saved and tipe_kendaraan: 
                    kendaraan.delete()
                    return render(request, 'kendaraan/kendaraan_form.html', {
                        'kendaraan_form': kendaraan_form, 
                        'mobil_form': mobil_form, 
                        'motor_form': motor_form
                    })
                
                return redirect('kendaraan:daftar_kendaraan')
        
        # --- PERUBAHAN NAMA TEMPLATE (Form Invalid) ---
        return render(request, 'kendaraan/kendaraan_form.html', {
            'kendaraan_form': kendaraan_form, 
            'mobil_form': mobil_form, 
            'motor_form': motor_form
        })
    
    # GET request
    # --- PERUBAHAN NAMA TEMPLATE (GET Request) ---
    return render(request, 'kendaraan/kendaraan_form.html', {
        'kendaraan_form': kendaraan_form, 
        'mobil_form': mobil_form, 
        'motor_form': motor_form,
        'is_edit': False
    })


# UPDATE (Edit Kendaraan + Detail Mobil/Motor) - FUNCTION BASED VIEW
def edit_kendaraan(request, pk):
    # ... (Logika deteksi tipe kendaraan) ...
    kendaraan = get_object_or_404(Kendaraan, pk=pk)
    detail_instance = None
    DetailForm = None
    tipe = None
    
    if kendaraan.cek_mobil:
        detail_instance = kendaraan.detail_mobil
        DetailForm = MobilForm
        tipe = 'Mobil'
    elif kendaraan.cek_motor:
        detail_instance = kendaraan.detail_motor
        DetailForm = MotorForm
        tipe = 'Motor'
    
    kendaraan_form = KendaraanForm(request.POST or None, request.FILES or None, instance=kendaraan)
    if DetailForm:
        detail_form = DetailForm(request.POST or None, instance=detail_instance)
    else:
        detail_form = None

    if request.method == 'POST':
        if kendaraan_form.is_valid() and (not DetailForm or detail_form.is_valid()):
            with transaction.atomic():
                kendaraan_form.save()
                if DetailForm:
                    detail_form.save()
            return redirect('kendaraan:detail_kendaraan', pk=kendaraan.pk)
    
    # GET request atau form invalid
    # --- PERUBAHAN NAMA TEMPLATE ---
    return render(request, 'kendaraan/kendaraan_form.html', {
        'kendaraan_form': kendaraan_form, 
        'detail_form': detail_form, 
        'kendaraan': kendaraan,
        'tipe': tipe,
        'is_edit': True # Tambahkan flag ini untuk penyesuaian di template
    })

# DELETE (Hapus Kendaraan) - CLASS BASED VIEW
class HapusKendaraanView(DeleteView):
    model = Kendaraan
    # --- PERUBAHAN NAMA TEMPLATE ---
    template_name = 'kendaraan/kendaraan_confirm_delete.html' 
    context_object_name = 'kendaraan'
    success_url = reverse_lazy('kendaraan:daftar_kendaraan')


# ===== Garasi CRUD (Focus on kendaraan_ext app) =====
class DaftarGarasiView(ListView):
    model = Garasi
    template_name = 'garasi/garasi_list.html'
    context_object_name = 'daftar_garasi'


class DetailGarasiView(DetailView):
    model = Garasi
    template_name = 'garasi/garasi_detail.html'
    context_object_name = 'garasi'


class TambahGarasiView(ListView):
    # Use a simple CreateView-like implementation using function approach
    # but here we use a CreateView to keep code concise.
    pass


from django.views.generic.edit import CreateView, UpdateView


class TambahGarasiView(CreateView):
    model = Garasi
    form_class = GarasiForm
    template_name = 'garasi/garasi_form.html'
    success_url = reverse_lazy('kendaraan:garasi_list')


class EditGarasiView(UpdateView):
    model = Garasi
    form_class = GarasiForm
    template_name = 'garasi/garasi_form.html'
    context_object_name = 'form'
    success_url = reverse_lazy('kendaraan:garasi_list')


class HapusGarasiView(DeleteView):
    model = Garasi
    template_name = 'garasi/garasi_confirm_delete.html'
    context_object_name = 'garasi'
    success_url = reverse_lazy('kendaraan:garasi_list')


# ===== Mobil CRUD =====
class DaftarMobilView(ListView):
    model = Mobil
    template_name = 'mobil/mobil_list.html'
    context_object_name = 'daftar_mobil'


class DetailMobilView(DetailView):
    model = Mobil
    template_name = 'mobil/mobil_detail.html'
    context_object_name = 'mobil'


class TambahMobilView(CreateView):
    model = Mobil
    form_class = MobilForm
    template_name = 'mobil/mobil_form.html'
    success_url = reverse_lazy('kendaraan:mobil_list')


class EditMobilView(UpdateView):
    model = Mobil
    form_class = MobilForm
    template_name = 'mobil/mobil_form.html'
    success_url = reverse_lazy('kendaraan:mobil_list')


class HapusMobilView(DeleteView):
    model = Mobil
    template_name = 'mobil/mobil_confirm_delete.html'
    context_object_name = 'mobil'
    success_url = reverse_lazy('kendaraan:mobil_list')


# ===== Motor CRUD =====
class DaftarMotorView(ListView):
    model = Motor
    template_name = 'motor/motor_list.html'
    context_object_name = 'daftar_motor'


class DetailMotorView(DetailView):
    model = Motor
    template_name = 'motor/motor_detail.html'
    context_object_name = 'motor'


class TambahMotorView(CreateView):
    model = Motor
    form_class = MotorForm
    template_name = 'motor/motor_form.html'
    success_url = reverse_lazy('kendaraan:motor_list')


class EditMotorView(UpdateView):
    model = Motor
    form_class = MotorForm
    template_name = 'motor/motor_form.html'
    success_url = reverse_lazy('kendaraan:motor_list')


class HapusMotorView(DeleteView):
    model = Motor
    template_name = 'motor/motor_confirm_delete.html'
    context_object_name = 'motor'
    success_url = reverse_lazy('kendaraan:motor_list')


    