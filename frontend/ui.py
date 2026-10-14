import os
import time
import tkinter as tk
from tkinter import messagebox, ttk

from backend.m1_pesanan import M1Pesanan
from backend.m2_antrean import M2Antrean, proses_kasir
from backend.m3_laporan import M3Laporan


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2EZ4U Food Delivery")
        self.geometry("1100x700")
        self.minsize(980, 620)

        self.m1 = M1Pesanan()
        self.m2 = M2Antrean(self.m1)
        self.m3 = M3Laporan()
        self.aksi = "M1_LIHAT"

        self._buat_tampilan()
        self.after(100, self._muat_data)

    def _buat_tampilan(self):
        tk.Label(self, text="2EZ4U Food Delivery", font=("Arial", 16, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")

        utama = tk.Frame(self)
        utama.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        kiri = tk.Frame(utama, width=280, bd=1, relief="solid")
        kiri.pack(side="left", fill="y", padx=(0, 10))
        kiri.pack_propagate(False)

        kanan = tk.Frame(utama, bd=1, relief="solid")
        kanan.pack(side="left", fill="both", expand=True)

        self._menu(kiri, "M1 - PESANAN", (
            ("Lihat pesanan", "M1_LIHAT"),
            ("Tambah REGULER", "M1_REGULER"),
            ("Tambah PRIORITAS", "M1_PRIORITAS"),
            ("Tambah VIP", "M1_VIP"),
            ("Hapus pesanan", "M1_HAPUS"),
        ))
        self._menu(kiri, "M2 - STACK & QUEUE", (
            ("Stack - Postfix kasir", "M2_POSTFIX"),
            ("Stack - Undo", "M2_UNDO"),
            ("Stack - Redo", "M2_REDO"),
            ("Queue - Enqueue", "M2_ENQUEUE"),
            ("Queue - Dequeue naif", "M2_DN"),
            ("Queue - Dequeue circular", "M2_DC"),
        ))
        self._menu(kiri, "M3 - SORT & SEARCH", (
            ("Sort - Insertion sort", "M3_INSERT"),
            ("Sort - Merge sort", "M3_MERGE"),
            ("Search - Linear search", "M3_LINEAR"),
            ("Search - Binary search", "M3_BINARY"),
        ))

        ttk.Separator(kiri, orient="horizontal").pack(fill="x", padx=8, pady=8)
        self.status = tk.Label(kiri, text="Memuat data...", justify="left", anchor="w", wraplength=250)
        self.status.pack(fill="x", padx=10, pady=(0, 8))

        self.form = tk.Frame(kanan)
        self.form.pack(fill="x", padx=16, pady=12)
        self.judulaksi = tk.Label(self.form, text="", font=("Arial", 12, "bold"))
        self.judulaksi.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.label1 = tk.Label(self.form, text="")
        self.entry1 = tk.Entry(self.form, width=42)
        self.label2 = tk.Label(self.form, text="")
        self.entry2 = tk.Entry(self.form, width=42)
        self.label3 = tk.Label(self.form, text="")
        self.entry3 = tk.Entry(self.form, width=42)
        self.label4 = tk.Label(self.form, text="")
        self.entry4 = tk.Entry(self.form, width=42)
        self.kunci = ttk.Combobox(self.form, values=("oid", "harga", "selesai"), state="readonly", width=18)
        self.kunci.set("harga")
        self.jalankan = tk.Button(self.form, text="JALANKAN", width=16, command=self._jalankan)

        tk.Label(kanan, text="HASIL", font=("Arial", 10, "bold")).pack(anchor="w", padx=16)
        self.hasil = tk.Text(kanan, wrap="none", state="disabled")
        self.hasil.pack(fill="both", expand=True, padx=16, pady=(5, 10))

        tk.Label(kanan, text="COMMAND / WAKTU", font=("Arial", 10, "bold")).pack(anchor="w", padx=16)
        self.command = tk.Text(kanan, height=7, wrap="word", state="disabled")
        self.command.pack(fill="x", padx=16, pady=(5, 14))

        self._atur_form()

    def _menu(self, parent, judul, items):
        tk.Label(parent, text=judul, font=("Arial", 10, "bold"), anchor="w", padx=8, pady=5).pack(fill="x")
        for teks, kode in items:
            tk.Button(parent, text=teks, anchor="w", padx=10, command=lambda k=kode: self._pilih(k)).pack(fill="x", padx=8, pady=1)

    def _muat_data(self):
        try:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lokasi = os.path.join(root, "data", "pesanan.csv")
            mulai = time.perf_counter()
            jumlah = self.m1.muat_csv(lokasi)
            antre = self.m2.muat_dari_array(self.m1.array)
            self.m3.muat_dari_array(self.m1.array)
            durasi = time.perf_counter() - mulai
            self._update_status()
            self._tulis_command(f"Data siap: {jumlah:,} pesanan, {antre:,} berstatus ANTRE ({durasi:.2f} detik)")
        except Exception as exc:
            messagebox.showerror("Gagal memuat data", str(exc))

    def _update_status(self):
        n1, n2, cap, geser, undo, redo = self.m2.stats()
        self.status.config(text=(
            f"M1 data: {len(self.m1.array):,}\n"
            f"Queue naif: {n1:,}\n"
            f"Queue circular: {n2:,}\n"
            f"Circular cap: {cap:,}\n"
            f"Undo/redo: {undo}/{redo}\n"
            f"Geseran naif: {geser:,}"
        ))

    def _pilih(self, aksi):
        self.aksi = aksi
        self._atur_form()

    def _sembunyi(self):
        for w in (self.label1, self.entry1, self.label2, self.entry2, self.label3, self.entry3, self.label4, self.entry4, self.kunci, self.jalankan):
            w.grid_forget()

    def _field(self, baris, label, entry, teks, isi=""):
        label.config(text=teks)
        label.grid(row=baris, column=0, sticky="w", padx=(0, 12), pady=4)
        entry.grid(row=baris, column=1, sticky="w", pady=4)
        entry.delete(0, "end")
        if isi != "":
            entry.insert(0, isi)

    def _atur_form(self):
        self._sembunyi()
        pasangan = (
            ("M1_LIHAT", "M1 - Lihat pesanan"),
            ("M1_REGULER", "M1 - Tambah pesanan REGULER"),
            ("M1_PRIORITAS", "M1 - Tambah pesanan PRIORITAS"),
            ("M1_VIP", "M1 - Tambah pesanan VIP"),
            ("M1_HAPUS", "M1 - Hapus pesanan"),
            ("M2_POSTFIX", "M2 - Stack: infix ke postfix dan hitung"),
            ("M2_UNDO", "M2 - Undo aksi terakhir"),
            ("M2_REDO", "M2 - Redo aksi terakhir"),
            ("M2_ENQUEUE", "M2 - Queue: enqueue"),
            ("M2_DN", "M2 - Queue: dequeue naif"),
            ("M2_DC", "M2 - Queue: dequeue circular"),
            ("M3_INSERT", "M3 - Insertion sort"),
            ("M3_MERGE", "M3 - Merge sort"),
            ("M3_LINEAR", "M3 - Linear search"),
            ("M3_BINARY", "M3 - Binary search"),
        )
        judul = self.aksi
        for kode, teks in pasangan:
            if kode == self.aksi:
                judul = teks
                break
        self.judulaksi.config(text=judul)

        if self.aksi in ("M1_LIHAT", "M1_HAPUS"):
            self._field(1, self.label1, self.entry1, "Nomor urut pesanan", "1")
            self.jalankan.grid(row=2, column=1, sticky="w", pady=8)

        elif self.aksi in ("M1_REGULER", "M1_PRIORITAS", "M1_VIP", "M2_ENQUEUE"):
            self._field(1, self.label1, self.entry1, "Nama pelanggan")
            self._field(2, self.label2, self.entry2, "Restoran")
            self._field(3, self.label3, self.entry3, "Menu")
            self._field(4, self.label4, self.entry4, "Harga", "10000")
            self.jalankan.grid(row=5, column=1, sticky="w", pady=8)

        elif self.aksi == "M2_POSTFIX":
            self._field(1, self.label1, self.entry1, "Ekspresi", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
            self.jalankan.grid(row=2, column=1, sticky="w", pady=8)

        elif self.aksi in ("M2_DN", "M2_DC"):
            self._field(1, self.label1, self.entry1, "Jumlah dequeue", "1")
            self.jalankan.grid(row=2, column=1, sticky="w", pady=8)

        elif self.aksi in ("M3_INSERT", "M3_MERGE"):
            default = "2000" if self.aksi == "M3_INSERT" else "4000"
            self._field(1, self.label1, self.entry1, "Jumlah data", default)
            self.label2.config(text="Kunci")
            self.label2.grid(row=2, column=0, sticky="w", padx=(0, 12), pady=4)
            self.kunci.grid(row=2, column=1, sticky="w", pady=4)
            self.jalankan.grid(row=3, column=1, sticky="w", pady=8)

        elif self.aksi in ("M3_LINEAR", "M3_BINARY"):
            self._field(1, self.label1, self.entry1, "OID yang dicari", "O-137442")
            self.jalankan.grid(row=2, column=1, sticky="w", pady=8)

        else:
            self.jalankan.grid(row=1, column=1, sticky="w", pady=8)

    def _buat_pesanan(self, prioritas=3):
        nama = self.entry1.get().strip()
        resto = self.entry2.get().strip()
        menu = self.entry3.get().strip()
        harga = self.entry4.get().strip()
        if nama == "" or resto == "" or menu == "" or not harga.isdigit():
            raise ValueError("Isi data pesanan dengan benar")
        sekarang = time.localtime()
        detik = sekarang.tm_hour * 3600 + sekarang.tm_min * 60 + sekarang.tm_sec
        return self.m1.buat_pesanan_baru(nama, resto, menu, int(harga), prioritas, detik)

    def _jalankan(self):
        try:
            if self.aksi == "M1_LIHAT":
                index = int(self.entry1.get()) - 1
                a, b, ta, tb = self.m1.lihat(index)
                self._tulis_hasil("ARRAY\n" + a.ringkas() + "\n\nLINKED LIST\n" + b.ringkas())
                self._tulis_command(f"M1 lihat | array {ta:.6f} ms | linked list {tb:.6f} ms")

            elif self.aksi == "M1_HAPUS":
                data, ta, tb = self.m1.hapus(int(self.entry1.get()) - 1)
                self._tulis_hasil("Dihapus:\n" + data.ringkas())
                self._tulis_command(f"M1 hapus | array {ta:.6f} ms | linked list {tb:.6f} ms")

            elif self.aksi in ("M1_REGULER", "M1_PRIORITAS", "M1_VIP"):
                prioritas = 3 if self.aksi == "M1_REGULER" else 2 if self.aksi == "M1_PRIORITAS" else 1
                p = self._buat_pesanan(prioritas)
                if prioritas == 3:
                    ta, tb = self.m1.tambah_regular(p)
                    self.m2.catat_order(p, "REGULER")
                elif prioritas == 2:
                    ta, tb = self.m1.tambah_prioritas(p)
                    self.m2.catat_order(p, "PRIORITAS")
                else:
                    ta, tb = self.m1.tambah_vip(p)
                    self.m2.catat_order(p, "VIP")
                self._tulis_hasil(p.ringkas())
                self._tulis_command(f"M1 tambah prioritas {prioritas} | array {ta:.6f} ms | linked list {tb:.6f} ms")

            elif self.aksi == "M2_POSTFIX":
                postfix, total, langkah, waktu = proses_kasir(self.entry1.get())
                teks = "postfix: " + " ".join(postfix) + f"\nTOTAL: Rp {total:,.0f}\n\n"
                for baris in langkah[:40]:
                    teks += f"{baris[0]:>8} | {baris[1]:16} | stack: {baris[2]:14} | {baris[3]}\n"
                self._tulis_hasil(teks)
                self._tulis_command(f"M2 stack postfix | {waktu:.4f} ms")

            elif self.aksi == "M2_ENQUEUE":
                p = self._buat_pesanan(3)
                tn, tc = self.m2.enqueue(p)
                self._tulis_hasil(p.ringkas())
                self._tulis_command(f"M2 enqueue | naif {tn:.6f} ms | circular {tc:.6f} ms")

            elif self.aksi == "M2_DN":
                n = int(self.entry1.get())
                keluar, geser, waktu = self.m2.dequeue_naif(n)
                self._tulis_hasil(self._daftar_pesanan(keluar))
                self._tulis_command(f"M2 dequeue naif | keluar {len(keluar)} | geser {geser:,} | {waktu:.4f} ms")

            elif self.aksi == "M2_DC":
                n = int(self.entry1.get())
                keluar, waktu = self.m2.dequeue_circular(n)
                self._tulis_hasil(self._daftar_pesanan(keluar))
                self._tulis_command(f"M2 dequeue circular | keluar {len(keluar)} | geser 0 | {waktu:.4f} ms")

            elif self.aksi == "M2_UNDO":
                mulai = time.perf_counter_ns()
                teks = self.m2.undo_last()
                waktu = (time.perf_counter_ns() - mulai) / 1_000_000
                self._tulis_hasil(teks)
                self._tulis_command(f"M2 undo | {waktu:.4f} ms")

            elif self.aksi == "M2_REDO":
                mulai = time.perf_counter_ns()
                teks = self.m2.redo_last()
                waktu = (time.perf_counter_ns() - mulai) / 1_000_000
                self._tulis_hasil(teks)
                self._tulis_command(f"M2 redo | {waktu:.4f} ms")

            elif self.aksi in ("M3_INSERT", "M3_MERGE"):
                jumlah = int(self.entry1.get())
                kunci = self.kunci.get()
                if self.aksi == "M3_INSERT":
                    data, banding, pindah, waktu = self.m3.sort_insertion(jumlah, kunci)
                    nama = "insertion sort"
                else:
                    data, banding, pindah, waktu = self.m3.sort_merge(jumlah, kunci)
                    nama = "merge sort"
                self._tulis_hasil(self._hasil_sort(data, kunci))
                self._tulis_command(f"M3 {nama} | n={len(data):,} | {banding:,} perbandingan | {pindah:,} pemindahan | {waktu:.3f} ms")

            elif self.aksi == "M3_LINEAR":
                oid = self.entry1.get().strip()
                item, index, banding, waktu = self.m3.cari_linear(oid)
                self._hasil_cari(item, index, banding, waktu, "linear")

            elif self.aksi == "M3_BINARY":
                oid = self.entry1.get().strip()
                item, index, banding, waktu, baru, waktu_sort, banding_sort = self.m3.cari_binary(oid)
                ekstra = ""
                if baru:
                    ekstra = f" | index oid dibuat dulu {waktu_sort:.2f} ms ({banding_sort:,} perbandingan sort)"
                self._hasil_cari(item, index, banding, waktu, "binary", ekstra)

            self._update_status()

        except Exception as exc:
            messagebox.showwarning("Tidak bisa dijalankan", str(exc))

    def _hasil_cari(self, item, index, banding, waktu, nama, ekstra=""):
        if item is None:
            self._tulis_hasil("Data tidak ditemukan")
        else:
            self._tulis_hasil(item.ringkas())
        self._tulis_command(f"M3 {nama} search | index {index} | {banding:,} perbandingan | {waktu:.4f} ms{ekstra}")

    def _hasil_sort(self, data, kunci):
        teks = f"10 data pertama setelah diurutkan berdasarkan {kunci}:\n\n"
        batas = 10 if len(data) > 10 else len(data)
        i = 0
        while i < batas:
            p = data[i]
            selesai = "-" if p.t_selesai_detik is None else str(p.t_selesai_detik)
            teks += f"{i + 1:>2}. {p.oid} | harga {p.harga:>6} | selesai {selesai}\n"
            i += 1
        return teks

    def _daftar_pesanan(self, data):
        if len(data) == 0:
            return "Antrean kosong"
        teks = ""
        batas = 10 if len(data) > 10 else len(data)
        i = 0
        while i < batas:
            teks += data[i].ringkas() + "\n"
            i += 1
        if len(data) > batas:
            teks += f"... dan {len(data) - batas} pesanan lain"
        return teks

    def _tulis_hasil(self, teks):
        self.hasil.config(state="normal")
        self.hasil.delete("1.0", "end")
        self.hasil.insert("end", teks)
        self.hasil.config(state="disabled")

    def _tulis_command(self, teks):
        self.command.config(state="normal")
        self.command.delete("1.0", "end")
        self.command.insert("end", teks)
        self.command.config(state="disabled")


