from bppgen.data.stats import Cooccurrence
import unittest

class TestCooccurrence(unittest.TestCase):

    def test_basic(self):
        coocs = Cooccurrence(4)
        coocs.add([1, 2, 3, 4, 5])
        coocs.add([1, 3, 4, 10])
        coocs.add([1, 3, 4, 10, 11])
        coocs.add([1, 4, 10, 16])
        coocs.add([12, 13])
        self.assertEqual(coocs.prob([16]), 0.2)
        self.assertEqual(coocs.cond_prob([4], [2]), 1)
        self.assertEqual(coocs.cond_prob([2], [4]), 0.25)
        self.assertEqual(coocs.cond_prob([12], [1]), 0)
        self.assertEqual(coocs.cond_prob([13], [1]), 0)
        self.assertTrue(coocs.pmi([13], [12]) > coocs.pmi([1], [3]))

    def test_add_bipartite(self):
        coocs = Cooccurrence(2)
        coocs.add_bipartite([1, 2, 3, 4], [5, 6, 7, 8])
        coocs.add_bipartite([1, 2], [5, 6, 7, 9])
        self.assertEqual(coocs.prob([1]), 1)
        self.assertEqual(coocs.prob([1, 2]), 0.0)
        self.assertEqual(coocs.prob([7, 3]), 0.5)

    def test_add_record(self):
        coocs = Cooccurrence(2)
        coocs.add_record([[1, 2]])
        coocs.add_record([[1, 3], [1, 2]])
        
        self.assertEqual(coocs.prob([1]), 1)
        self.assertEqual(coocs.prob([3]), 0.5)
        self.assertEqual(coocs.prob([1, 3]), 0.5)
        



        


if __name__ == '__main__' :
    unittest.main()