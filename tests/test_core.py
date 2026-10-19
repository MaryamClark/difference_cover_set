import unittest

from difference_cover_set import DifferenceCoverSet


class TestBasic(unittest.TestCase):
    def test_insert_and_contains(self):
        s = DifferenceCoverSet()
        self.assertTrue(s.insert(5))
        self.assertFalse(s.insert(5))
        self.assertIn(5, s)
        self.assertNotIn(6, s)

    def test_delete(self):
        s = DifferenceCoverSet()
        s.insert(10)
        self.assertTrue(s.delete(10))
        self.assertFalse(s.delete(10))
        self.assertNotIn(10, s)

    def test_len(self):
        s = DifferenceCoverSet()
        for v in [3, 1, 4, 1, 5]:
            s.insert(v)
        self.assertEqual(len(s), 4)


class TestRangeQueries(unittest.TestCase):
    def test_count_in_range(self):
        s = DifferenceCoverSet()
        for v in [2, 4, 6, 8, 10]:
            s.insert(v)
        self.assertEqual(s.count_in_range(3, 7), 2)
        self.assertEqual(s.count_in_range(0, 100), 5)
        self.assertEqual(s.count_in_range(5, 5), 0)

    def test_kth_smallest_basic(self):
        s = DifferenceCoverSet()
        for v in [10, 20, 30, 40, 50]:
            s.insert(v)
        self.assertEqual(s.kth_smallest_in_range(0, 100, 1), 10)
        self.assertEqual(s.kth_smallest_in_range(0, 100, 3), 30)
        self.assertEqual(s.kth_smallest_in_range(0, 100, 5), 50)

    def test_kth_smallest_in_subrange(self):
        s = DifferenceCoverSet()
        for v in [1, 3, 5, 7, 9, 11]:
            s.insert(v)
        self.assertEqual(s.kth_smallest_in_range(4, 9, 1), 5)
        self.assertEqual(s.kth_smallest_in_range(4, 9, 2), 7)
        self.assertEqual(s.kth_smallest_in_range(4, 9, 3), 9)

    def test_kth_out_of_range_raises(self):
        s = DifferenceCoverSet()
        s.insert(1)
        s.insert(2)
        with self.assertRaises(ValueError):
            s.kth_smallest_in_range(0, 10, 3)
        with self.assertRaises(ValueError):
            s.kth_smallest_in_range(0, 10, 0)

    def test_empty_range_raises(self):
        s = DifferenceCoverSet()
        s.insert(1)
        with self.assertRaises(ValueError):
            s.kth_smallest_in_range(5, 3, 1)


class TestGrowth(unittest.TestCase):
    def test_grow_universe(self):
        s = DifferenceCoverSet(universe_size=16)
        self.assertTrue(s.insert(1000))
        self.assertIn(1000, s)
        self.assertEqual(s.kth_smallest_in_range(0, 2000, 1), 1000)

    def test_negative_insert_raises(self):
        s = DifferenceCoverSet()
        with self.assertRaises(ValueError):
            s.insert(-1)


class TestIter(unittest.TestCase):
    def test_iter_sorted(self):
        s = DifferenceCoverSet()
        vals = [7, 2, 5, 1, 9]
        for v in vals:
            s.insert(v)
        self.assertEqual(list(s), sorted(vals))


class TestEdgeCases(unittest.TestCase):
    def test_duplicate_inserts(self):
        s = DifferenceCoverSet()
        self.assertTrue(s.insert(3))
        self.assertFalse(s.insert(3))
        self.assertEqual(len(s), 1)

    def test_delete_then_reinsert(self):
        s = DifferenceCoverSet()
        s.insert(8)
        s.delete(8)
        self.assertTrue(s.insert(8))
        self.assertEqual(len(s), 1)

    def test_range_with_no_elements(self):
        s = DifferenceCoverSet()
        s.insert(100)
        self.assertEqual(s.count_in_range(0, 50), 0)
        with self.assertRaises(ValueError):
            s.kth_smallest_in_range(0, 50, 1)

    def test_single_element_queries(self):
        s = DifferenceCoverSet()
        s.insert(42)
        self.assertEqual(s.count_in_range(42, 42), 1)
        self.assertEqual(s.kth_smallest_in_range(42, 42, 1), 42)
        with self.assertRaises(ValueError):
            s.kth_smallest_in_range(42, 42, 2)


if __name__ == "__main__":
    unittest.main()
