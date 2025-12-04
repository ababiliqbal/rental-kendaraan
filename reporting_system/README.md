# Reporting System Documentation

## Overview
Reporting System adalah sebuah modul Django yang menyediakan fitur pelaporan komprehensif untuk aplikasi rental kendaraan. Sistem ini memungkinkan pengguna untuk membuat, melihat, dan mengelola berbagai jenis laporan.

## Fitur Utama

### 1. Revenue Report (Laporan Pendapatan)
- Total pendapatan dalam periode tertentu
- Jumlah total pemesanan
- Pemesanan yang selesai, dibatalkan, dan pending
- Nilai rata-rata pemesanan

### 2. Booking Report (Laporan Pemesanan)
- Total pemesanan
- Status pemesanan (selesai, dibatalkan, pending)
- Kendaraan paling sering disewa
- Pengguna paling aktif

### 3. Vehicle Report (Laporan Kendaraan)
- Total kendaraan
- Kendaraan yang tersedia
- Kendaraan yang sedang disewa
- Kendaraan dalam perawatan

### 4. User Report (Laporan Pengguna)
- Total pengguna
- Pengguna aktif
- Pengguna baru (30 hari terakhir)
- Rata-rata pemesanan per pengguna

### 5. Maintenance Report (Laporan Perawatan)
- Total pemeliharaan
- Pemeliharaan yang selesai
- Pemeliharaan yang pending
- Total biaya perawatan

## Struktur File

```
reporting_system/
├── __init__.py
├── admin.py           # Django admin configuration
├── apps.py            # App configuration
├── forms.py           # Form definitions
├── models.py          # Database models
├── tests.py           # Unit tests
├── urls.py            # URL routing
├── utils.py           # Utility functions
├── views.py           # View functions
├── migrations/        # Database migrations
│   ├── __init__.py
│   └── 0001_initial.py
└── templates/
    ├── dashboard.html
    ├── revenue_report.html
    ├── booking_report.html
    ├── vehicle_report.html
    ├── user_report.html
    ├── report_list.html
    ├── report_detail.html
    └── report_confirm_delete.html
```

## Models

### Report
Model utama untuk semua laporan
- `report_type`: Jenis laporan (revenue, booking, kendaraan, user, maintenance)
- `title`: Judul laporan
- `description`: Deskripsi laporan
- `created_by`: User yang membuat laporan
- `status`: Status laporan (draft, published, archived)
- `start_date`: Tanggal mulai periode
- `end_date`: Tanggal akhir periode
- `file_path`: File laporan (opsional)

### RevenueReport
Detail laporan pendapatan
- `total_revenue`: Total pendapatan
- `total_bookings`: Total pemesanan
- `average_booking_value`: Nilai rata-rata pemesanan

### BookingReport
Detail laporan pemesanan
- `total_bookings`: Total pemesanan
- `most_booked_vehicle`: Kendaraan paling sering disewa
- `most_active_user`: Pengguna paling aktif

### VehicleReport
Detail laporan kendaraan
- `total_vehicles`: Total kendaraan
- `available_vehicles`: Kendaraan tersedia
- `rented_vehicles`: Kendaraan disewa

### UserReport
Detail laporan pengguna
- `total_users`: Total pengguna
- `active_users`: Pengguna aktif
- `average_bookings_per_user`: Rata-rata pemesanan per pengguna

### MaintenanceReport
Detail laporan perawatan
- `total_maintenance`: Total pemeliharaan
- `total_cost`: Total biaya

## URL Routes

```
/reports/                    - Dashboard reporting
/reports/revenue/           - Revenue report
/reports/booking/           - Booking report
/reports/vehicle/           - Vehicle report
/reports/user/              - User report
/reports/reports/           - List of all reports
/reports/reports/<id>/      - Detail report
/reports/reports/<id>/delete/ - Delete report
```

## Views

### Dashboard (`report_dashboard`)
Menampilkan overview sistem reporting dengan statistik umum.

### Revenue Report (`revenue_report`)
Menampilkan laporan pendapatan dengan filter tanggal.

### Booking Report (`booking_report`)
Menampilkan laporan pemesanan dengan analisis detail.

### Vehicle Report (`vehicle_report`)
Menampilkan laporan status kendaraan.

### User Report (`user_report`)
Menampilkan laporan statistik pengguna.

### Report List (`report_list`)
Menampilkan daftar semua laporan yang telah dibuat.

## Utility Functions

### `generate_revenue_report()`
Membuat laporan pendapatan otomatis

### `generate_booking_report()`
Membuat laporan pemesanan otomatis

### `generate_vehicle_report()`
Membuat laporan kendaraan otomatis

### `generate_user_report()`
Membuat laporan pengguna otomatis

### `get_revenue_summary()`
Mendapatkan ringkasan revenue dalam periode tertentu

### `get_top_vehicles()`
Mendapatkan top kendaraan yang paling sering disewa

### `get_top_users()`
Mendapatkan top pengguna yang paling sering booking

## Installation

1. App sudah terdaftar di `INSTALLED_APPS` dalam `settings.py`

2. Jalankan migrasi:
```bash
python manage.py migrate reporting_system
```

3. Akses dashboard reporting di:
```
http://localhost:8000/reports/
```

## Permissions

- `view_report`: Untuk melihat laporan
- `add_report`: Untuk membuat laporan
- `change_report`: Untuk mengubah laporan
- `delete_report`: Untuk menghapus laporan

## Testing

Jalankan test dengan:
```bash
python manage.py test reporting_system
```

## Notes

- Semua laporan memerlukan autentikasi user
- Laporan hanya bisa dihapus oleh pembuat laporan atau admin
- Data laporan diambil real-time dari database
- File laporan dapat di-export (fitur akan datang)

## Future Features

- Export laporan ke PDF
- Export laporan ke Excel
- Scheduling report generation
- Email report distribution
- Advanced analytics dan charts
- Custom report builder
