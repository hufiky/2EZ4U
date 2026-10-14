from time import perf_counter_ns

from backend.m1_pesanan import DynamicArray


class Tumpukan:
    def __init__(self):
        self.data = DynamicArray()

    def __len__(self):
        return len(self.data)

    def kosong(self):
        return len(self.data) == 0

    def push(self, nilai):
        self.data.append(nilai)

    def pop(self):
        if self.kosong():
            raise IndexError("Tumpukan kosong")
        i = len(self.data) - 1
        nilai = self.data.get(i)
        self.data.size -= 1
        self.data.data[self.data.size] = None
        return nilai

    def peek(self):
        if self.kosong():
            return None
        return self.data.get(len(self.data) - 1)


class AntreanNaif:
    def __init__(self):
        self.data = DynamicArray()
        self.total_geser = 0

    def __len__(self):
        return len(self.data)

    def enqueue(self, nilai):
        self.data.append(nilai)

    def dequeue(self):
        if len(self.data) == 0:
            return None, 0
        geser = len(self.data) - 1
        nilai = self.data.delete(0)
        self.total_geser += geser
        return nilai, geser

    def hapus_belakang(self):
        if len(self.data) == 0:
            return None
        return self.data.delete(len(self.data) - 1)

    def tambah_depan(self, daftar):
        i = len(daftar) - 1
        while i >= 0:
            self.data.insert_front(daftar[i])
            i -= 1


class AntreanMelingkar:
    def __init__(self, kapasitas=8):
        if kapasitas < 1:
            kapasitas = 1
        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0

    def __len__(self):
        return self.count

    @property
    def capacity(self):
        return len(self.data)

    def kosong(self):
        return self.count == 0

    def _tumbuh(self):
        lama = self.data
        kapasitas_lama = len(lama)
        baru = [None] * (kapasitas_lama * 2)

        i = 0
        while i < self.count:
            baru[i] = lama[(self.front + i) % kapasitas_lama]
            i += 1

        self.data = baru
        self.front = 0
        self.rear = self.count

    def enqueue(self, nilai):
        if self.count == len(self.data):
            self._tumbuh()

        self.data[self.rear] = nilai
        self.rear = (self.rear + 1) % len(self.data)
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None

        nilai = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % len(self.data)
        self.count -= 1
        return nilai

    def hapus_belakang(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % len(self.data)
        nilai = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return nilai

    def tambah_depan(self, daftar):
        butuh = self.count + len(daftar)
        while butuh > len(self.data):
            self._tumbuh()

        i = len(daftar) - 1
        while i >= 0:
            self.front = (self.front - 1) % len(self.data)
            self.data[self.front] = daftar[i]
            self.count += 1
            i -= 1


class M2Antrean:
    def __init__(self, m1=None):
        self.m1 = m1
        self.naif = AntreanNaif()
        self.circular = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()

    @staticmethod
    def _ms(ns):
        return ns / 1_000_000

    def muat_dari_array(self, array):
        i = 0
        masuk = 0
        while i < len(array):
            p = array.get(i)
            if p.status == "ANTRE":
                self.naif.enqueue(p)
                self.circular.enqueue(p)
                masuk += 1
            i += 1
        return masuk

    def _kosongkan_redo(self):
        while not self.redo.kosong():
            self.redo.pop()

    def catat_order(self, pesanan, jenis):
        self.undo.push(("ORDER", pesanan, jenis))
        self._kosongkan_redo()

    def _cari_order(self, oid):
        if self.m1 is None:
            return -1
        i = 0
        while i < len(self.m1.array):
            if self.m1.array.get(i).oid == oid:
                return i
            i += 1
        return -1

    def enqueue(self, pesanan, catat=True):
        mulai = perf_counter_ns()
        self.naif.enqueue(pesanan)
        waktu_naif = perf_counter_ns() - mulai

        mulai = perf_counter_ns()
        self.circular.enqueue(pesanan)
        waktu_circular = perf_counter_ns() - mulai

        if catat:
            self.undo.push(("ENQUEUE", pesanan))
            self._kosongkan_redo()

        return self._ms(waktu_naif), self._ms(waktu_circular)

    def dequeue_naif(self, jumlah=1, catat=True):
        if jumlah < 1:
            raise ValueError("Jumlah dequeue minimal 1")
        keluar = []
        geser = 0
        mulai = perf_counter_ns()

        i = 0
        while i < jumlah:
            nilai, banyak = self.naif.dequeue()
            if nilai is None:
                break
            keluar.append(nilai)
            geser += banyak
            i += 1

        waktu = perf_counter_ns() - mulai

        if catat and len(keluar) > 0:
            self.undo.push(("DEQUEUE_NAIF", keluar))
            self._kosongkan_redo()

        return keluar, geser, self._ms(waktu)

    def dequeue_circular(self, jumlah=1, catat=True):
        if jumlah < 1:
            raise ValueError("Jumlah dequeue minimal 1")
        keluar = []
        mulai = perf_counter_ns()

        i = 0
        while i < jumlah:
            nilai = self.circular.dequeue()
            if nilai is None:
                break
            keluar.append(nilai)
            i += 1

        waktu = perf_counter_ns() - mulai

        if catat and len(keluar) > 0:
            self.undo.push(("DEQUEUE_CIRCULAR", keluar))
            self._kosongkan_redo()

        return keluar, self._ms(waktu)

    def undo_last(self):
        if self.undo.kosong():
            return "Tidak ada aksi yang bisa di-undo"

        aksi = self.undo.pop()
        jenis = aksi[0]

        if jenis == "ORDER":
            if self.m1 is None:
                raise RuntimeError("M1 belum terhubung")
            p = aksi[1]
            index = self._cari_order(p.oid)
            if index == -1:
                raise RuntimeError("Pesanan untuk undo tidak ditemukan")
            self.m1.hapus(index)
            teks = p.oid + " dihapus lagi dari daftar pesanan"

        elif jenis == "ENQUEUE":
            p = aksi[1]
            a = self.naif.hapus_belakang()
            b = self.circular.hapus_belakang()
            if a is None or b is None:
                raise RuntimeError("Antrean tidak konsisten saat undo")
            teks = p.oid + " dikeluarkan lagi dari belakang"

        elif jenis == "DEQUEUE_NAIF":
            daftar = aksi[1]
            self.naif.tambah_depan(daftar)
            teks = str(len(daftar)) + " pesanan dikembalikan ke depan antrean naif"

        else:
            daftar = aksi[1]
            self.circular.tambah_depan(daftar)
            teks = str(len(daftar)) + " pesanan dikembalikan ke depan antrean circular"

        self.redo.push(aksi)
        return teks

    def redo_last(self):
        if self.redo.kosong():
            return "Tumpukan redo kosong, tidak ada yang diulang"

        aksi = self.redo.pop()
        jenis = aksi[0]

        if jenis == "ORDER":
            if self.m1 is None:
                raise RuntimeError("M1 belum terhubung")
            p = aksi[1]
            cara = aksi[2]
            if cara == "REGULER":
                self.m1.tambah_regular(p)
            elif cara == "PRIORITAS":
                self.m1.tambah_prioritas(p)
            else:
                self.m1.tambah_vip(p)
            teks = p.oid + " ditambahkan kembali ke daftar pesanan"

        elif jenis == "ENQUEUE":
            p = aksi[1]
            self.enqueue(p, catat=False)
            teks = p.oid + " masuk kembali ke belakang"

        elif jenis == "DEQUEUE_NAIF":
            jumlah = len(aksi[1])
            keluar, _, _ = self.dequeue_naif(jumlah, catat=False)
            aksi = ("DEQUEUE_NAIF", keluar)
            teks = str(len(keluar)) + " pesanan keluar lagi dari antrean naif"

        else:
            jumlah = len(aksi[1])
            keluar, _ = self.dequeue_circular(jumlah, catat=False)
            aksi = ("DEQUEUE_CIRCULAR", keluar)
            teks = str(len(keluar)) + " pesanan keluar lagi dari antrean circular"

        self.undo.push(aksi)
        return teks

    def history(self):
        hasil = []
        i = 0
        while i < len(self.undo.data):
            aksi = self.undo.data.get(i)
            hasil.append(aksi[0])
            i += 1
        return hasil

    def stats(self):
        return (
            len(self.naif),
            len(self.circular),
            self.circular.capacity,
            self.naif.total_geser,
            len(self.undo),
            len(self.redo),
        )


def _token(ekspresi):
    hasil = []
    angka = ""

    i = 0
    while i < len(ekspresi):
        c = ekspresi[i]
        if c.isdigit():
            angka += c
        else:
            if angka != "":
                hasil.append(angka)
                angka = ""
            if c in "+-*/()":
                hasil.append(c)
            elif not c.isspace():
                raise ValueError("Karakter tidak dikenali: " + c)
        i += 1

    if angka != "":
        hasil.append(angka)
    return hasil


def _prioritas(op):
    if op == "+" or op == "-":
        return 1
    if op == "*" or op == "/":
        return 2
    return 0


def ke_postfix(ekspresi):
    operator = Tumpukan()
    keluar = []
    langkah = []

    for item in _token(ekspresi):
        if item.isdigit():
            keluar.append(item)
            langkah.append((item, "angka keluar", _isi_stack(operator), " ".join(keluar)))

        elif item == "(":
            operator.push(item)
            langkah.append((item, "push (", _isi_stack(operator), " ".join(keluar)))

        elif item == ")":
            while not operator.kosong() and operator.peek() != "(":
                keluar.append(operator.pop())
            if operator.kosong():
                raise ValueError("Tanda kurung tidak seimbang")
            operator.pop()
            langkah.append((item, "pop sampai (", _isi_stack(operator), " ".join(keluar)))

        else:
            while (
                not operator.kosong()
                and operator.peek() != "("
                and _prioritas(operator.peek()) >= _prioritas(item)
            ):
                keluar.append(operator.pop())
            operator.push(item)
            langkah.append((item, "operator", _isi_stack(operator), " ".join(keluar)))

    while not operator.kosong():
        op = operator.pop()
        if op == "(":
            raise ValueError("Tanda kurung tidak seimbang")
        keluar.append(op)

    return keluar, langkah


def _isi_stack(stack):
    teks = []
    i = 0
    while i < len(stack.data):
        teks.append(str(stack.data.get(i)))
        i += 1
    return " ".join(teks)


def hitung(postfix):
    angka = Tumpukan()

    for item in postfix:
        if item.isdigit():
            angka.push(float(item))
            continue

        if len(angka) < 2:
            raise ValueError("Ekspresi postfix tidak valid")

        b = angka.pop()
        a = angka.pop()

        if item == "+":
            angka.push(a + b)
        elif item == "-":
            angka.push(a - b)
        elif item == "*":
            angka.push(a * b)
        elif item == "/":
            if b == 0:
                raise ZeroDivisionError("Pembagian dengan nol")
            angka.push(a / b)
        else:
            raise ValueError("Operator tidak dikenali")

    if len(angka) != 1:
        raise ValueError("Ekspresi postfix tidak valid")
    return angka.pop()


def proses_kasir(ekspresi):
    mulai = perf_counter_ns()
    postfix, langkah = ke_postfix(ekspresi)
    total = hitung(postfix)
    waktu = (perf_counter_ns() - mulai) / 1_000_000
    return postfix, total, langkah, waktu
