from time import perf_counter_ns


def ambil_kunci(pesanan, kunci):
    if kunci == "oid":
        return pesanan.oid
    if kunci == "harga":
        return pesanan.harga
    if kunci == "selesai":
        if pesanan.t_selesai_detik is None:
            return 10**12
        return pesanan.t_selesai_detik
    raise ValueError("Kunci sort tidak dikenali")


def insertion_sort(data, kunci):
    banding = 0
    pindah = 0
    i = 1

    while i < len(data):
        item = data[i]
        key = ambil_kunci(item, kunci)
        j = i - 1

        while j >= 0:
            banding += 1
            if ambil_kunci(data[j], kunci) > key:
                data[j + 1] = data[j]
                pindah += 1
                j -= 1
            else:
                break

        data[j + 1] = item
        pindah += 1
        i += 1

    return banding, pindah


def merge_sort(data, kunci):
    n = len(data)
    temp = [None] * n
    hitung = [0, 0]

    def gabung(lo, mid, hi):
        i = lo
        j = mid
        k = lo

        while i < mid and j < hi:
            hitung[0] += 1
            if ambil_kunci(data[i], kunci) <= ambil_kunci(data[j], kunci):
                temp[k] = data[i]
                i += 1
            else:
                temp[k] = data[j]
                j += 1
            hitung[1] += 1
            k += 1

        while i < mid:
            temp[k] = data[i]
            i += 1
            k += 1
            hitung[1] += 1

        while j < hi:
            temp[k] = data[j]
            j += 1
            k += 1
            hitung[1] += 1

        k = lo
        while k < hi:
            data[k] = temp[k]
            k += 1
            hitung[1] += 1

    def urut(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        urut(lo, mid)
        urut(mid, hi)
        gabung(lo, mid, hi)

    urut(0, n)
    return hitung[0], hitung[1]


def linear_search(data, target, kunci="oid"):
    banding = 0
    i = 0
    while i < len(data):
        banding += 1
        if ambil_kunci(data[i], kunci) == target:
            return i, banding
        i += 1
    return -1, banding


def binary_search(data, target, kunci="oid"):
    lo = 0
    hi = len(data) - 1
    banding = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        nilai = ambil_kunci(data[mid], kunci)
        banding += 1

        if nilai == target:
            return mid, banding
        if nilai < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, banding


class M3Laporan:
    def __init__(self):
        self.data = []
        self.data_oid = None
        self.waktu_index_oid = 0.0
        self.banding_index_oid = 0

    def muat_dari_array(self, array):
        self.data = [None] * len(array)
        i = 0
        while i < len(array):
            self.data[i] = array.get(i)
            i += 1
        self.data_oid = None
        return len(self.data)

    def _salin(self, jumlah):
        if jumlah < 1:
            raise ValueError("Jumlah data minimal 1")
        if jumlah > len(self.data):
            jumlah = len(self.data)

        hasil = [None] * jumlah
        i = 0
        while i < jumlah:
            hasil[i] = self.data[i]
            i += 1
        return hasil

    def sort_insertion(self, jumlah, kunci):
        if jumlah > 20000:
            raise ValueError("Insertion sort dibatasi 20.000 baris. Gunakan merge sort untuk data besar.")
        data = self._salin(jumlah)
        mulai = perf_counter_ns()
        banding, pindah = insertion_sort(data, kunci)
        waktu = (perf_counter_ns() - mulai) / 1_000_000
        return data, banding, pindah, waktu

    def sort_merge(self, jumlah, kunci):
        data = self._salin(jumlah)
        mulai = perf_counter_ns()
        banding, pindah = merge_sort(data, kunci)
        waktu = (perf_counter_ns() - mulai) / 1_000_000
        return data, banding, pindah, waktu

    def cari_linear(self, oid):
        mulai = perf_counter_ns()
        index, banding = linear_search(self.data, oid, "oid")
        waktu = (perf_counter_ns() - mulai) / 1_000_000
        item = None if index == -1 else self.data[index]
        return item, index, banding, waktu

    def _buat_index_oid(self):
        data = self._salin(len(self.data))
        mulai = perf_counter_ns()
        banding, _ = merge_sort(data, "oid")
        self.waktu_index_oid = (perf_counter_ns() - mulai) / 1_000_000
        self.banding_index_oid = banding
        self.data_oid = data

    def cari_binary(self, oid):
        baru = False
        if self.data_oid is None:
            self._buat_index_oid()
            baru = True

        mulai = perf_counter_ns()
        index, banding = binary_search(self.data_oid, oid, "oid")
        waktu = (perf_counter_ns() - mulai) / 1_000_000
        item = None if index == -1 else self.data_oid[index]
        return item, index, banding, waktu, baru, self.waktu_index_oid, self.banding_index_oid
