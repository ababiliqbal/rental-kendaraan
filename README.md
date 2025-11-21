# Sistem Rental Kendaraan

Deskripsi singkat
-----------------
Repositori ini berisi aplikasi manajemen rental kendaraan yang dikembangkan dengan Django. Proyek dibuat untuk keperluan tugas besar mata kuliah Pemrograman Berorientasi Objek (PBO) dan mencakup modul untuk pengelolaan armada, pelanggan, pegawai, transaksi, dan pelaporan.

Ikhtisar dokumentasi
--------------------
- Fitur utama
- Instruksi instalasi dan menjalankan secara lokal
- Panduan kolaborasi (Git)
- Struktur proyek
- Perintah Django yang sering digunakan

Fitur utama
------------
- Manajemen kendaraan (mobil/motor): data, ketersediaan, dan harga sewa.
- Registrasi dan otentikasi pelanggan; proses pemesanan dan riwayat.
- Panel administrasi untuk staf (konfirmasi pengembalian, denda, pembayaran).
- Pelaporan pendapatan dan kinerja operasional.

Prasyarat
---------
- Python 3.8 atau lebih baru.
- Git untuk kontrol versi.

Direkomendasikan menggunakan virtual environment (`venv`) untuk mengisolasi dependensi.

Instalasi dan menjalankan (local)
---------------------------------
1. Clone repository

```powershell
git clone https://github.com/ababiliqbal/rental-kendaraan.git
cd rental-kendaraan
```

2. Buat virtual environment

```powershell
python -m venv venv
```

3. Aktifkan virtual environment

```powershell
venv\Scripts\activate
```

4. Install dependensi

```powershell
pip install -r requirements.txt
```

5. Siapkan database (migrasi)

```powershell
python manage.py makemigrations
python manage.py migrate
```

6. Buat akun administrator (superuser)

```powershell
python manage.py createsuperuser
```

7. Jalankan server pengembangan

```powershell
python manage.py runserver
```

Buka `http://127.0.0.1:8000/` di browser.

Panduan kolaborasi (Git)
------------------------
Untuk mengurangi konflik, ikuti alur kerja branch ini:

- Perbarui `main` sebelum mulai bekerja:

```powershell
git checkout main
git pull origin main
```

- Buat branch baru untuk fitur/perbaikan:

```powershell
git checkout -b fitur/nama-fitur
```

- Commit perubahan dengan pesan yang jelas:

```powershell
git add .
git commit -m "Deskripsi singkat perubahan"
```

- Push branch dan ajukan Pull Request untuk review:

```powershell
git push origin fitur/nama-fitur
```

Setelah direview dan diuji, lakukan merge melalui GitHub.

Struktur proyek (ringkasan)
--------------------------
- `manage.py`  utilitas manajemen Django.
- `rental_project/`  konfigurasi proyek (mis. `settings.py`, `urls.py`).
- `rental_app/`  aplikasi utama berisi `models.py`, `views.py`, `urls.py`, dan `templates/`.
- `db.sqlite3`  basis data lokal (jika digunakan untuk development, hindari mengunggah data sensitif).

Perintah Django yang sering digunakan
-----------------------------------
- `python manage.py runserver`  jalankan server pengembangan.
- `python manage.py makemigrations`  buat berkas migrasi dari perubahan model.
- `python manage.py migrate`  terapkan migrasi ke database.
- `python manage.py createsuperuser`  buat akun admin Django.
- `pip freeze > requirements.txt`  perbarui daftar dependensi.

Catatan
------
- Jangan mengunggah file berisi kredensial atau kunci (mis. `.env`) ke repository publik.
- Jika menggunakan `db.sqlite3` untuk development, pastikan file tersebut dikecualikan saat perlu.
