from django.views.generic import ListView
from .models import Mobil, Motor, Garasi, KendaraanExt

class MobilListView(ListView):
    model = Mobil
    template_name = "kendaraan_ext/mobil_list.html"
    context_object_name = "mobil_list"

class MotorListView(ListView):
    model = Motor
    template_name = "kendaraan_ext/motor_list.html"
    context_object_name = "motor_list"

class GarasiListView(ListView):
    model = Garasi
    template_name = "kendaraan_ext/garasi_list.html"
    context_object_name = "garasi_list"

class KendaraanExtListView(ListView):
    model = KendaraanExt
    template_name = "kendaraan_ext/kendaraanext_list.html"
    context_object_name = "kendaraanext_list"
