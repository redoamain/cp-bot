# Bot Telegram Laporan Perusahaan

Bot Telegram ini dirancang untuk memudahkan pembuatan laporan perusahaan secara otomatis. Cukup kirim perintah dengan parameter yang sesuai, bot akan mengambil data dari database SQL Server dan mengirimkan file Excel laporan langsung ke chat Telegram Anda.

## Fitur

- **Laporan Buku Besar** – Generate laporan buku besar berdasarkan periode tanggal.
- **Laporan Kartu Stok** – Melihat mutasi stok barang.
- **Laporan PO Pembelian** – Daftar purchase order pembelian.
- **Laporan PO Produksi** – Daftar purchase order produksi.
- **Laporan Stok** – Rekap stok barang.
- **Mudah digunakan** – Cukup ketik perintah dengan format yang sudah ditentukan.
- **File Excel** – Semua laporan dikirim dalam format `.xlsx` dengan styling rapi.

## Persyaratan

- Python 3.8 atau lebih baru
- Database SQL Server (dengan stored procedure yang diperlukan)
- Token bot Telegram (dapatkan dari [@BotFather](https://t.me/botfather))

## 

1. **Struktur Aplikasi**  
   ```bash
   .
    ├── app
    │   ├── config
    │   │   └── settings.py       # Konfigurasi darienvironment
    │   ├── database
        │      └── connection.py         # Koneksi ke SQL Server
    │   ├── handlers
    │   │   ├── start.py              # Perintah /start
    │   │   ├── buku_besar.py         # Perintah /bukubesar
    │   │   ├── kartu_stok.py         # Perintah /kartustok
    │   │   ├── po_beli.py            # Perintah /pobeli
    │   │   ├── po_prod.py            # Perintah /poprod
    │   │   └── stok.py               # Perintah /stok
    │   └── utils
    │       └── helpers.py            # Fungsi pembantu (format tanggal, dll)
    ├── main.py                        # Inisialisasi dan registrasi handler
    ├── run.py                         # Entry point untuk menjalankan bot
    ├── .env                            # Environment variables (tidak di-commit)
    ├── .envex                          # Contoh file environment
    ├── requirements.txt                # Daftar dependensi Python
    └── README.md                       # Dokumentasi ini