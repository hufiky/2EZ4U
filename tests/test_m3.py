import unittest

from backend.m1_pesanan import Pesanan
from backend.m3_laporan import binary_search, insertion_sort, linear_search, merge_sort


def p(oid, harga, selesai=10):
    return Pesanan(oid, oid, "resto", "menu", harga, 3, 0, selesai, "DONE")


class TestSort(unittest.TestCase):
    def test_insertion_sort(self):
        data = [p("O-3", 30), p("O-1", 10), p("O-2", 20)]
        banding, _ = insertion_sort(data, "harga")
        self.assertEqual([x.harga for x in data], [10, 20, 30])
        self.assertGreater(banding, 0)

    def test_merge_sort(self):
        data = [p("O-3", 30), p("O-1", 10), p("O-2", 20), p("O-4", 10)]
        merge_sort(data, "harga")
        self.assertEqual([x.harga for x in data], [10, 10, 20, 30])
        self.assertEqual([data[0].oid, data[1].oid], ["O-1", "O-4"])

    def test_hasil_sort_sama(self):
        awal = [p("O-4", 40), p("O-2", 20), p("O-3", 20), p("O-1", 10)]
        a = list(awal)
        b = list(awal)
        insertion_sort(a, "harga")
        merge_sort(b, "harga")
        self.assertEqual([x.oid for x in a], [x.oid for x in b])

    def test_insertion_stabil(self):
        data = [p("O-1", 10), p("O-2", 10), p("O-3", 5)]
        insertion_sort(data, "harga")
        self.assertEqual([x.oid for x in data], ["O-3", "O-1", "O-2"])

    def test_merge_variasi_data(self):
        kasus = (
            ([5, 1, 4, 2, 3], [1, 2, 3, 4, 5]),
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([3, 1, 3, 2, 1], [1, 1, 2, 3, 3]),
        )
        for angka, benar in kasus:
            data = [p("O-" + str(i), v) for i, v in enumerate(angka)]
            merge_sort(data, "harga")
            self.assertEqual([x.harga for x in data], benar)


class TestSearch(unittest.TestCase):
    def test_linear(self):
        data = [p("O-1", 10), p("O-2", 20), p("O-3", 30)]
        index, banding = linear_search(data, "O-3")
        self.assertEqual(index, 2)
        self.assertEqual(banding, 3)

    def test_binary(self):
        data = [p("O-1", 10), p("O-2", 20), p("O-3", 30), p("O-4", 40), p("O-5", 50)]
        self.assertEqual(binary_search(data, "O-3")[0], 2)
        self.assertEqual(binary_search(data, "O-1")[0], 0)
        self.assertEqual(binary_search(data, "O-5")[0], 4)
        self.assertEqual(binary_search(data, "O-9")[0], -1)
        self.assertEqual(binary_search([], "O-1")[0], -1)


if __name__ == "__main__":
    unittest.main()
