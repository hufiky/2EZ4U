import csv
from time import perf_counter_ns


class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas,
                 t_masuk_detik, t_selesai_detik, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas
        self.t_masuk_detik = t_masuk_detik
        self.t_selesai_detik = t_selesai_detik
        self.status = status

    def ringkas(self):
        return (
            f"{self.oid} | {self.pelanggan} | {self.resto} | {self.menu} | "
            f"Rp{self.harga:,} | prioritas {self.prioritas} | {self.status}"
        )


class DynamicArray:
    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self.capacity = kapasitas
        self.size = 0
        self.data = [None] * kapasitas

    def __len__(self):
        return self.size

    def _cek_index(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Indeks pesanan di luar rentang")

    def _resize(self):
        kapbaru = self.capacity * 2
        databaru = [None] * kapbaru

        i = 0
        while i < self.size:
            databaru[i] = self.data[i]
            i += 1

        self.data = databaru
        self.capacity = kapbaru

    def get(self, index):
        self._cek_index(index)
        return self.data[index]

    def append(self, item):
        if self.size == self.capacity:
            self._resize()

        self.data[self.size] = item
        self.size += 1

    def insert_at(self, index, item):
        if index < 0 or index > self.size:
            raise IndexError("Indeks penyisipan di luar rentang")

        if self.size == self.capacity:
            self._resize()

        i = self.size
        while i > index:
            self.data[i] = self.data[i - 1]
            i -= 1

        self.data[index] = item
        self.size += 1

    def insert_front(self, item):
        self.insert_at(0, item)

    def delete(self, index):
        self._cek_index(index)
        hasil = self.data[index]

        i = index
        while i < self.size - 1:
            self.data[i] = self.data[i + 1]
            i += 1

        self.size -= 1
        self.data[self.size] = None
        return hasil


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __len__(self):
        return self.size

    def _cek_index(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Indeks pesanan di luar rentang")

    def get(self, index):
        self._cek_index(index)

        jalan = self.head
        i = 0
        while i < index:
            jalan = jalan.next
            i += 1

        return jalan.data

    def append(self, item):
        nodebaru = Node(item)

        if self.head is None:
            self.head = nodebaru
            self.tail = nodebaru
        else:
            self.tail.next = nodebaru
            self.tail = nodebaru

        self.size += 1

    def insert_front(self, item):
        nodebaru = Node(item)
        nodebaru.next = self.head
        self.head = nodebaru

        if self.tail is None:
            self.tail = nodebaru

        self.size += 1

    def insert_at(self, index, item):
        if index < 0 or index > self.size:
            raise IndexError("Indeks penyisipan di luar rentang")

        if index == 0:
            self.insert_front(item)
            return

        if index == self.size:
            self.append(item)
            return

        sebelum = self.head
        i = 1
        while i < index:
            sebelum = sebelum.next
            i += 1

        nodebaru = Node(item)
        nodebaru.next = sebelum.next
        sebelum.next = nodebaru
        self.size += 1

    def delete(self, index):
        self._cek_index(index)

        if index == 0:
            hasil = self.head.data
            self.head = self.head.next
            self.size -= 1

            if self.size == 0:
                self.tail = None

            return hasil

        sebelum = self.head
        i = 1
        while i < index:
            sebelum = sebelum.next
            i += 1

        target = sebelum.next
        sebelum.next = target.next

        if target is self.tail:
            self.tail = sebelum

        self.size -= 1
        return target.data


class M1Pesanan:
    def __init__(self):
        self.array = DynamicArray()
        self.linked_list = LinkedList()
        self.nomorbaru = 1

    def muat_csv(self, filepath):
        jumlah = 0
        terbesar = 0

        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            if header is None:
                return 0

            for row in reader:
                if len(row) < 9:
                    continue

                selesai = None
                if row[7] != "":
                    selesai = int(row[7])

                p = Pesanan(
                    row[0], row[1], row[2], row[3], int(row[4]), int(row[5]),
                    int(row[6]), selesai, row[8]
                )

                self.array.append(p)
                self.linked_list.append(p)
                jumlah += 1

                if row[0].startswith("O-"):
                    try:
                        nomor = int(row[0][2:])
                        if nomor > terbesar:
                            terbesar = nomor
                    except ValueError:
                        pass

        self.nomorbaru = terbesar + 1
        return jumlah

    def _buat_oid(self):
        oid = "O-" + str(self.nomorbaru).zfill(6)
        self.nomorbaru += 1
        return oid

    def buat_pesanan_baru(self, pelanggan, resto, menu, harga, prioritas,
                           t_masuk_detik=0):
        return Pesanan(
            self._buat_oid(),
            pelanggan.strip(),
            resto.strip(),
            menu.strip(),
            int(harga),
            int(prioritas),
            int(t_masuk_detik),
            None,
            "ANTRE",
        )

    @staticmethod
    def _ke_ms(ns):
        return ns / 1_000_000

    def _cek_sinkron(self):
        if len(self.array) != len(self.linked_list):
            raise RuntimeError("Array dan Linked List tidak sinkron")

    def lihat(self, index):
        self._cek_sinkron()

        mulai = perf_counter_ns()
        a = self.array.get(index)
        ta = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        l = self.linked_list.get(index)
        tl = perf_counter_ns() - mulai

        return a, l, self._ke_ms(ta), self._ke_ms(tl)

    def tambah_regular(self, pesanan):
        mulai = perf_counter_ns()
        self.array.append(pesanan)
        ta = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        self.linked_list.append(pesanan)
        tl = perf_counter_ns() - mulai

        return self._ke_ms(ta), self._ke_ms(tl)

    def tambah_prioritas(self, pesanan):
        tengahA = len(self.array) // 2
        tengahL = len(self.linked_list) // 2

        mulai = perf_counter_ns()
        self.array.insert_at(tengahA, pesanan)
        ta = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        self.linked_list.insert_at(tengahL, pesanan)
        tl = perf_counter_ns() - mulai

        return self._ke_ms(ta), self._ke_ms(tl)

    def tambah_vip(self, pesanan):
        mulai = perf_counter_ns()
        self.array.insert_front(pesanan)
        ta = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        self.linked_list.insert_front(pesanan)
        tl = perf_counter_ns() - mulai

        return self._ke_ms(ta), self._ke_ms(tl)

    def hapus(self, index):
        self._cek_sinkron()

        mulai = perf_counter_ns()
        a = self.array.delete(index)
        ta = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        l = self.linked_list.delete(index)
        tl = perf_counter_ns() - mulai

        if a.oid != l.oid:
            raise RuntimeError("Isi Array dan Linked List tidak lagi sama")

        return a, self._ke_ms(ta), self._ke_ms(tl)
