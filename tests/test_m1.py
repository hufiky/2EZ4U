import unittest

from backend.m1_pesanan import DynamicArray, LinkedList


class TestDynamicArray(unittest.TestCase):
    def test_append_dan_resize(self):
        data = DynamicArray(2)
        data.append("A")
        data.append("B")
        data.append("C")

        self.assertEqual(len(data), 3)
        self.assertGreaterEqual(data.capacity, 3)
        self.assertEqual(data.get(0), "A")
        self.assertEqual(data.get(2), "C")

    def test_insert_dan_hapus(self):
        data = DynamicArray()
        data.append("A")
        data.append("B")
        data.insert_front("X")
        data.insert_at(2, "Y")

        self.assertEqual(data.get(0), "X")
        self.assertEqual(data.get(2), "Y")
        self.assertEqual(data.delete(1), "A")
        self.assertEqual(data.get(1), "Y")


class TestLinkedList(unittest.TestCase):
    def test_head_dan_tail(self):
        data = LinkedList()
        data.append("A")
        data.append("B")

        self.assertEqual(data.head.data, "A")
        self.assertEqual(data.tail.data, "B")
        self.assertEqual(len(data), 2)

    def test_insert_dan_hapus(self):
        data = LinkedList()
        data.append("A")
        data.append("B")
        data.insert_front("X")
        data.insert_at(2, "Y")

        self.assertEqual(data.get(0), "X")
        self.assertEqual(data.get(2), "Y")
        self.assertEqual(data.delete(3), "B")
        self.assertEqual(data.tail.data, "Y")

    def test_hapus_satu_node(self):
        data = LinkedList()
        data.append("A")
        self.assertEqual(data.delete(0), "A")
        self.assertIsNone(data.head)
        self.assertIsNone(data.tail)
        self.assertEqual(len(data), 0)


if __name__ == "__main__":
    unittest.main()
