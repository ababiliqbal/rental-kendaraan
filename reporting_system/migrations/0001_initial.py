# Generated migration for reporting_system models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kendaraan_ext', '0001_initial'),
        ('manajemen_pengguna', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('revenue', 'Revenue Report'), ('booking', 'Booking Report'), ('kendaraan', 'Vehicle Report'), ('user', 'User Report'), ('maintenance', 'Maintenance Report')], max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('file_path', models.FileField(blank=True, null=True, upload_to='reports/')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='VehicleReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_vehicles', models.IntegerField(default=0)),
                ('available_vehicles', models.IntegerField(default=0)),
                ('rented_vehicles', models.IntegerField(default=0)),
                ('maintenance_vehicles', models.IntegerField(default=0)),
                ('total_value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_report', to='reporting_system.report')),
            ],
            options={
                'verbose_name': 'Vehicle Report',
                'verbose_name_plural': 'Vehicle Reports',
            },
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_users', models.IntegerField(default=0)),
                ('active_users', models.IntegerField(default=0)),
                ('new_users', models.IntegerField(default=0)),
                ('total_bookings_by_users', models.IntegerField(default=0)),
                ('average_bookings_per_user', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_report', to='reporting_system.report')),
            ],
            options={
                'verbose_name': 'User Report',
                'verbose_name_plural': 'User Reports',
            },
        ),
        migrations.CreateModel(
            name='RevenueReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_bookings', models.IntegerField(default=0)),
                ('total_completed', models.IntegerField(default=0)),
                ('total_cancelled', models.IntegerField(default=0)),
                ('average_booking_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='revenue_report', to='reporting_system.report')),
            ],
            options={
                'verbose_name': 'Revenue Report',
                'verbose_name_plural': 'Revenue Reports',
            },
        ),
        migrations.CreateModel(
            name='MaintenanceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_maintenance', models.IntegerField(default=0)),
                ('completed_maintenance', models.IntegerField(default=0)),
                ('pending_maintenance', models.IntegerField(default=0)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_report', to='reporting_system.report')),
            ],
            options={
                'verbose_name': 'Maintenance Report',
                'verbose_name_plural': 'Maintenance Reports',
            },
        ),
        migrations.CreateModel(
            name='BookingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_bookings', models.IntegerField(default=0)),
                ('completed_bookings', models.IntegerField(default=0)),
                ('cancelled_bookings', models.IntegerField(default=0)),
                ('pending_bookings', models.IntegerField(default=0)),
                ('most_active_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booking_reports', to=settings.AUTH_USER_MODEL)),
                ('most_booked_vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kendaraan_ext.kendaraan')),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking_report', to='reporting_system.report')),
            ],
            options={
                'verbose_name': 'Booking Report',
                'verbose_name_plural': 'Booking Reports',
            },
        ),
    ]
