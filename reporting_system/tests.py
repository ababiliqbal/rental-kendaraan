from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Report, RevenueReport


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_create_report(self):
        report = Report.objects.create(
            report_type='revenue',
            title='Test Revenue Report',
            created_by=self.user
        )
        self.assertEqual(report.title, 'Test Revenue Report')
        self.assertEqual(report.report_type, 'revenue')


class ReportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        # make user staff so they can access staff-only reporting views
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password')
    
    def test_dashboard_view(self):
        response = self.client.get(reverse('reporting_system:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_revenue_report_view(self):
        response = self.client.get(reverse('reporting_system:revenue_report'))
        self.assertEqual(response.status_code, 200)
    
    def test_booking_report_view(self):
        response = self.client.get(reverse('reporting_system:booking_report'))
        self.assertEqual(response.status_code, 200)
    
    def test_vehicle_report_view(self):
        response = self.client.get(reverse('reporting_system:vehicle_report'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_report_view(self):
        response = self.client.get(reverse('reporting_system:user_report'))
        self.assertEqual(response.status_code, 200)
