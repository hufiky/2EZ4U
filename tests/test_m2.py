import unittest

from backend.m1_pesanan import M1Pesanan, Pesanan
from backend.m2_antrean import AntreanMelingkar, AntreanNaif, M2Antrean, ke_postfix, hitung


def pesanan(oid):
    return Pesanan(oid, "Pelanggan", "resto", "menu", 10000, 3, 0, None, "ANTRE")


class TestStackKasir(unittest.TestCase):
    def test_postfix_dan_total(self):
        postfix, _ = ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        self.assertEqual(" ".join(postfix), "3 12000 * 2 8500 * + 5000 -")
        self.assertEqual(hitung(postfix), 48000)

    def test_urutan_minus_bagi(self):
        postfix, _ = ke_postfix("20 - 8 / 2")
        self.assertEqual(hitung(postfix), 16)


class TestQueue(unittest.TestCase):
    def test_naif(self):
        q = AntreanNaif()
        q.enqueue("A")
        q.enqueue("B")
        q.enqueue("C")
        nilai, geser = q.dequeue()
        self.assertEqual(nilai, "A")
        self.assertEqual(geser, 2)
        self.assertEqual(len(q), 2)

    def test_circular_wrap(self):
        q = AntreanMelingkar(4)
        q.enqueue("A")
        q.enqueue("B")
        q.enqueue("C")
        self.assertEqual(q.dequeue(), "A")
        self.assertEqual(q.dequeue(), "B")
        q.enqueue("D")
        q.enqueue("E")
        q.enqueue("F")
        hasil = []
        while not q.kosong():
            hasil.append(q.dequeue())
        self.assertEqual(hasil, ["C", "D", "E", "F"])

    def test_undo_redo_enqueue(self):
        m2 = M2Antrean()
        p = pesanan("O-000001")
        m2.enqueue(p)
        self.assertEqual(len(m2.naif), 1)
        self.assertEqual(len(m2.circular), 1)
        m2.undo_last()
        self.assertEqual(len(m2.naif), 0)
        self.assertEqual(len(m2.circular), 0)
        m2.redo_last()
        self.assertEqual(len(m2.naif), 1)
        self.assertEqual(len(m2.circular), 1)

    def test_undo_dequeue_circular(self):
        m2 = M2Antrean()
        for i in range(4):
            m2.naif.enqueue(pesanan("O-" + str(i)))
            m2.circular.enqueue(pesanan("O-" + str(i)))
        keluar, _ = m2.dequeue_circular(2)
        self.assertEqual(len(keluar), 2)
        self.assertEqual(len(m2.circular), 2)
        m2.undo_last()
        self.assertEqual(len(m2.circular), 4)
        self.assertEqual(m2.circular.dequeue().oid, "O-0")
        self.assertEqual(m2.circular.dequeue().oid, "O-1")

    def test_order_undo_redo(self):
        m1 = M1Pesanan()
        m2 = M2Antrean(m1)
        p = pesanan("O-000777")
        m1.tambah_vip(p)
        m2.catat_order(p, "VIP")
        self.assertEqual(len(m1.array), 1)
        m2.undo_last()
        self.assertEqual(len(m1.array), 0)
        m2.redo_last()
        self.assertEqual(len(m1.array), 1)

    def test_aksi_baru_mengosongkan_redo(self):
        m2 = M2Antrean()
        p1 = pesanan("O-1")
        p2 = pesanan("O-2")
        m2.enqueue(p1)
        m2.undo_last()
        self.assertEqual(len(m2.redo), 1)
        m2.enqueue(p2)
        self.assertEqual(len(m2.redo), 0)


if __name__ == "__main__":
    unittest.main()
