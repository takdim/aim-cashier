# Product Requirements Document (PRD)
## Website Kasir Berbasis Flask & MySQL

| | |
|---|---|
| **Versi** | 1.0.0 |
| **Status** | Draft |
| **Tanggal** | 16 Mei 2026 |
| **Penulis** | — |

---

## 1. Ringkasan Eksekutif

Website kasir ini adalah aplikasi berbasis web yang dibangun menggunakan **Flask** (Python) sebagai backend dan **MySQL** sebagai database. Aplikasi ini dirancang untuk membantu kasir toko dalam mengelola transaksi penjualan, stok produk, dan laporan keuangan secara efisien dan akurat.

---

## 2. Latar Belakang & Tujuan

### 2.1 Latar Belakang
Banyak usaha kecil dan menengah masih mengelola penjualan secara manual (buku kas atau spreadsheet), yang rawan kesalahan, sulit dipantau secara real-time, dan tidak efisien. Diperlukan sebuah sistem kasir digital yang mudah digunakan, ringan, dan dapat diakses melalui browser tanpa instalasi khusus.

### 2.2 Tujuan Produk
- Mempercepat proses transaksi penjualan di kasir
- Mengurangi kesalahan pencatatan manual
- Memberikan laporan penjualan harian, mingguan, dan bulanan secara otomatis
- Memudahkan pengelolaan stok produk secara terpusat

---

## 3. Pengguna (User)

| Peran | Deskripsi |
|---|---|
| **Admin** | Mengelola produk, kategori, pengguna, dan melihat semua laporan |
| **Kasir** | Melakukan transaksi penjualan dan melihat riwayat transaksi sendiri |

---

## 4. Fitur & Kebutuhan Fungsional

### 4.1 Modul Autentikasi
- [ ] Login dengan username dan password
- [ ] Logout
- [ ] Manajemen sesi pengguna (session-based dengan Flask)
- [ ] Role-based access control (Admin vs Kasir)
- [ ] Halaman tidak bisa diakses tanpa login (redirect ke halaman login)

### 4.2 Modul Manajemen Produk *(Admin)*
- [ ] Tambah produk baru (nama, kode/SKU, harga jual, harga beli, stok, kategori)
- [ ] Edit data produk
- [ ] Hapus produk (soft delete)
- [ ] Lihat daftar semua produk dengan filter dan pencarian
- [ ] Upload gambar produk (opsional)

### 4.3 Modul Kategori Produk *(Admin)*
- [ ] Tambah kategori
- [ ] Edit dan hapus kategori
- [ ] Lihat daftar kategori

### 4.4 Modul Kasir / Transaksi *(Kasir & Admin)*
- [ ] Pencarian produk berdasarkan nama atau kode
- [ ] Tambah produk ke keranjang belanja
- [ ] Ubah jumlah item di keranjang
- [ ] Hapus item dari keranjang
- [ ] Kalkulasi total harga otomatis
- [ ] Input jumlah uang diterima → tampil kembalian
- [ ] Proses pembayaran dan simpan transaksi ke database
- [ ] Cetak struk / nota transaksi (tampil di halaman atau export PDF)
- [ ] Stok produk otomatis berkurang setelah transaksi berhasil

### 4.5 Modul Manajemen Pengguna *(Admin)*
- [ ] Tambah akun kasir baru
- [ ] Edit data pengguna (nama, username, password, role)
- [ ] Nonaktifkan / hapus akun pengguna

### 4.6 Modul Laporan *(Admin)*
- [ ] Laporan penjualan harian
- [ ] Laporan penjualan per periode (filter tanggal)
- [ ] Laporan stok produk (produk dengan stok rendah)
- [ ] Rekap pendapatan total
- [ ] Export laporan ke format CSV atau PDF

### 4.7 Riwayat Transaksi
- [ ] Lihat semua riwayat transaksi (Admin)
- [ ] Lihat riwayat transaksi milik sendiri (Kasir)
- [ ] Detail transaksi per struk

---

## 5. Kebutuhan Non-Fungsional

| Kategori | Kebutuhan |
|---|---|
| **Performa** | Halaman harus loading dalam < 2 detik pada koneksi lokal |
| **Keamanan** | Password di-hash dengan bcrypt, proteksi CSRF pada semua form |
| **Kompatibilitas** | Berjalan di browser modern (Chrome, Firefox, Edge) |
| **Responsif** | Tampilan menyesuaikan layar desktop dan tablet |
| **Ketersediaan** | Dapat berjalan di jaringan lokal (localhost) maupun server |

---

## 6. Arsitektur Teknis

### 6.1 Stack Teknologi

| Layer | Teknologi |
|---|---|
| **Backend** | Python 3.x, Flask |
| **Database** | MySQL 8.x |
| **ORM** | SQLAlchemy / Flask-SQLAlchemy |
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript |
| **Autentikasi** | Flask-Login, Flask-Bcrypt |
| **Form Handling** | Flask-WTF |
| **Migrasi DB** | Flask-Migrate (Alembic) |
| **Template Engine** | Jinja2 |

### 6.2 Struktur Folder Proyek

```
kasir_app/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   └── transaction.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── product.py
│   │   ├── transaction.py
│   │   └── report.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── product/
│   │   ├── transaction/
│   │   └── report/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── migrations/
├── config.py
├── run.py
└── requirements.txt
```

### 6.3 Skema Database (Entitas Utama)

#### Tabel `users`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INT PK | Primary key |
| name | VARCHAR(100) | Nama lengkap |
| username | VARCHAR(50) UNIQUE | Username login |
| password_hash | VARCHAR(255) | Hash bcrypt |
| role | ENUM('admin','kasir') | Peran pengguna |
| is_active | BOOLEAN | Status akun |
| created_at | DATETIME | Waktu dibuat |

#### Tabel `categories`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INT PK | Primary key |
| name | VARCHAR(100) | Nama kategori |

#### Tabel `products`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INT PK | Primary key |
| sku | VARCHAR(50) UNIQUE | Kode produk |
| name | VARCHAR(200) | Nama produk |
| category_id | INT FK | Relasi ke categories |
| buy_price | DECIMAL(12,2) | Harga beli |
| sell_price | DECIMAL(12,2) | Harga jual |
| stock | INT | Stok tersedia |
| is_active | BOOLEAN | Status produk |

#### Tabel `transactions`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INT PK | Primary key |
| invoice_no | VARCHAR(50) UNIQUE | Nomor struk |
| user_id | INT FK | Kasir yang memproses |
| total_amount | DECIMAL(12,2) | Total transaksi |
| paid_amount | DECIMAL(12,2) | Uang diterima |
| change_amount | DECIMAL(12,2) | Kembalian |
| created_at | DATETIME | Waktu transaksi |

#### Tabel `transaction_items`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INT PK | Primary key |
| transaction_id | INT FK | Relasi ke transactions |
| product_id | INT FK | Relasi ke products |
| quantity | INT | Jumlah item |
| unit_price | DECIMAL(12,2) | Harga saat transaksi |
| subtotal | DECIMAL(12,2) | Subtotal item |

---

## 7. Alur Penggunaan (User Flow)

### Alur Transaksi Kasir
```
Login → Dashboard → Halaman Kasir
→ Cari Produk → Tambah ke Keranjang
→ Ulangi hingga semua item masuk
→ Input nominal bayar
→ Klik "Proses Pembayaran"
→ Tampil kembalian & struk
→ Transaksi selesai
```

### Alur Tambah Produk (Admin)
```
Login → Dashboard → Menu Produk
→ Klik "Tambah Produk"
→ Isi form (nama, SKU, harga, stok, kategori)
→ Simpan → Produk tampil di daftar
```

---

## 8. Halaman / Antarmuka (UI)

| No | Halaman | Akses |
|---|---|---|
| 1 | Login | Publik |
| 2 | Dashboard | Admin, Kasir |
| 3 | Halaman Kasir (POS) | Admin, Kasir |
| 4 | Daftar Produk | Admin |
| 5 | Tambah / Edit Produk | Admin |
| 6 | Daftar Kategori | Admin |
| 7 | Manajemen Pengguna | Admin |
| 8 | Riwayat Transaksi | Admin, Kasir |
| 9 | Detail Transaksi / Struk | Admin, Kasir |
| 10 | Laporan Penjualan | Admin |
| 11 | Laporan Stok | Admin |

---

## 9. Batasan & Asumsi

- Aplikasi dirancang untuk **satu toko / satu cabang** (tidak multi-cabang)
- Pembayaran hanya mendukung **tunai** (tidak ada integrasi payment gateway)
- Tidak ada fitur diskon atau promo pada versi awal (v1.0)
- Tidak ada fitur barcode scanner pada versi awal (input manual / pencarian teks)
- Aplikasi berjalan di **jaringan lokal** atau server sederhana (VPS)

---

## 10. Milestone & Estimasi Pengerjaan

| Fase | Deskripsi | Estimasi |
|---|---|---|
| **Fase 1** | Setup proyek, database, autentikasi | 3 hari |
| **Fase 2** | Manajemen produk & kategori | 3 hari |
| **Fase 3** | Halaman kasir & proses transaksi | 5 hari |
| **Fase 4** | Laporan & riwayat transaksi | 3 hari |
| **Fase 5** | Testing, bug fix, deploy | 3 hari |
| **Total** | | **~17 hari kerja** |

---

## 11. Kriteria Selesai (Definition of Done)

- [ ] Semua fitur pada bagian 4 berjalan tanpa error
- [ ] Semua halaman responsif di desktop dan tablet
- [ ] Data transaksi tersimpan dengan benar di MySQL
- [ ] Stok produk berkurang otomatis setelah transaksi
- [ ] Laporan menampilkan data yang akurat
- [ ] Kode sudah bersih, terdokumentasi, dan ada file `README.md`

---

*Dokumen ini bersifat hidup (living document) dan dapat diperbarui seiring perkembangan proyek.*
