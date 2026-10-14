# 2EZ4U App

2EZ4U merupakan project mata kuliah Struktur Data & Analisa Algoritma. Project ini mengambil contoh sederhana dari sistem delivery makanan, dengan fokus utama pada penerapan struktur data dan algoritma.

Untuk milestone pertama, saya mencoba menyimpan data pesanan menggunakan dua struktur data yang berbeda, yaitu dynamic array dan singly linked list. Data yang digunakan sama supaya cara kerja dan waktu proses keduanya bisa dibandingkan.

Pada M1 ada beberapa operasi dasar, yaitu melihat pesanan, menambah pesanan reguler di belakang, prioritas di tengah, vip di depan, serta menghapus pesanan.

Dari implementasi ini terlihat bahwa array lebih cepat ketika mengambil data berdasarkan index. Di sisi lain, linked list lebih sederhana ketika menambah data di depan karena tidak perlu menggeser seluruh data yang sudah ada.

Data pesanan diambil dari `data/pesanan.csv`, sedangkan implementasi utamanya berada di `backend/m1_pesanan.py`.

Untuk mengecek implementasi M1 dapat menjalankan:

```bash
python -m unittest tests.test_m1 -v