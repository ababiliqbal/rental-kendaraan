from django import forms
from .models import Report


class ReportFilterForm(forms.Form):
    """Form untuk filter laporan"""
    REPORT_TYPE_CHOICES = [('', 'All Types')] + list(Report.REPORT_TYPE_CHOICES)
    STATUS_CHOICES = [('', 'All Status')] + list(Report.STATUS_CHOICES)
    
    report_type = forms.ChoiceField(choices=REPORT_TYPE_CHOICES, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )


class RevenueReportFilterForm(forms.Form):
    """Form untuk filter revenue report"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )


class BookingReportFilterForm(forms.Form):
    """Form untuk filter booking report"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )


class CreateReportForm(forms.ModelForm):
    """Form untuk membuat laporan baru"""
    class Meta:
        model = Report
        fields = ['report_type', 'title', 'description', 'status', 'start_date', 'end_date']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
