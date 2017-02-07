import unittest
from bppgen.data.trie import Trie, CountingTrie

class TestTrie(unittest.TestCase):
    def test_trie(self):
        t = Trie()
        t.add('abcd', 1)
        t.add('abce', 2)
        self.assertEqual(t.get('abcd'), 1)
        self.assertTrue('abcd' in t)
        self.assertFalse('abc' in t)
        self.assertFalse('abcde' in t)
        self.assertEqual(t.get('abce'), 2)
    
    def test_count_trie(self):
        t = CountingTrie()
        t.add('abcd')
        t.add('abc')
        t.add('abcd')
        
        self.assertTrue('abcd' in t.trie)
        self.assertTrue('abcd' in t)
        self.assertFalse('ab' in t)
        self.assertTrue('abc' in t)
        self.assertEqual(t.get('abc'), 1)
        self.assertEqual(t.get('abcd'), 2)
        
    def test_find1(self):
        t = Trie()
        t.add([1, 2, 3], 1)
        t.add([1, 2, 2], 1)
        t.add([6, 6, 6, 6], 1)
        t.add([6, 6, 6], 1)
        t.add([1, 2, 4], 1)
        
        searched = [5, 1, 2, 3, 4, 6, 1, 2, 4]
        ranges = t.find(searched)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(searched[ranges[0][0]:ranges[0][1]], [1, 2, 3])
        self.assertEqual(searched[ranges[1][0]:ranges[1][1]], [1, 2, 4])
        
    def test_find2(self):
        t = Trie()
        t.add([6, 6, 6, 3], 1)
        t.add([6, 6, 6], 1)
        t.add([6, 1, 2], 1)
        
        searched = [6, 6, 6, 6, 1, 2]
        ranges = t.find(searched)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(searched[ranges[0][0]:ranges[0][1]], [6, 6, 6])
        self.assertEqual(searched[ranges[1][0]:ranges[1][1]], [6, 1, 2])
        
    def test_search_matches(self):
        t = Trie()
        t.add([6, 6, 6, 3], 1)
        t.add([6, 6, 6], 1)
        t.add([6, 1, 2], 1)
        
        searched = [6, 6, 6, 6, 1, 2]
        results = t.search(searched)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], [6, 6, 6])
        self.assertEqual(results[1], [6, 1, 2])
        
    def test_search_matches2(self):
        t = CountingTrie()
        t.add(["I", "am", "happy"])
        t.add(["it", "is", "sunny"])
        
        searched = "I am happy because it is sunny".split()
        
        results = t.search(searched)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ["I", "am", "happy"])
        self.assertEqual(results[1], ["it", "is", "sunny"])

    
    
if __name__ == '__main__':
    unittest.main()