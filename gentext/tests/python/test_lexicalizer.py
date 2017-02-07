from gentext.syntax import n, var, match
from gentext.lexicalizer import SimpleBilingualStructuralLexicalizer, TrivialEntityLexicalizer,\
    TrivialRelationLexicalizer, RotatingLexicon, simple_lexicalizer
import logging
import unittest
import testutils
from testutils import dummy_lexicon_en, DUMMY_RELATIONS
from gentext.aggregator import ConfiguredAggregator
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

logging.basicConfig(level=logging.DEBUG)

class TestStructural(unittest.TestCase):
    
    def test_juxtapose(self):
        l = SimpleBilingualStructuralLexicalizer({"coord_s" : n("C", "et")})
        tree1 = n("S", n("NP", n("N", "Marie")), n("VP", n("V", "dort")))
        tree2 = n("S", n("NP", n("N", "Marie")), n("VP", n("V", "mange")))
        trees = [tree1, tree2]
        self.assertEqual(l.clause_juxtaposition(trees), n("S", n("CP", n("C", "et"), tree1, tree2)))

    def test_juxtapose_same_subject(self):
        l = SimpleBilingualStructuralLexicalizer({"coord_s" : "et"})
        S1 = n("NP", n("N", "Marie"))
        tree1 = n("S", S1, n("VP", n("V", "dort")))
        VP2 = n("VP", n("V", "mange"))
        tree2 = n("S", n("NP", n("Pro", "il")), VP2)
        trees = [tree1, tree2]
        res = l.clause_juxtaposition_same_subject(trees)
        
    def test_juxtapose_same_subject2(self):
        l = SimpleBilingualStructuralLexicalizer({"coord_s" : n("C", "et")})
        S1 = n("NP", n("N", "Marie"))
        tree1 = n("S", S1, n("VP", n("V", "dormir")))
        VP2 = n("VP", n("V", "manger"))
        tree2 = n("S", n("NP", n("Pro", "je")), VP2)
        trees = [tree1, tree2]
        res = l.clause_juxtaposition_same_subject(trees)
        self.assertEqual(res.children[0].content["type"], "CP")
        self.assertEqual(res.children[0].children[0].content["type"], "C")
        self.assertEqual(res.children[0].children[1].content["type"], "S")
        self.assertEqual(res.children[0].children[1].children[0].content["type"], "NP")
        self.assertEqual(res.children[0].children[1].children[0].children[0].content["type"], "N")
        self.assertEqual(res.children[0].children[2].content["type"], "S")
        self.assertEqual(res.children[0].children[0].content["value"], "et")
        res = l.clause_juxtaposition_same_subject(trees, n("NP", n("Pro", "il", g="f")))
        
    def test_entity(self):
        l = SimpleBilingualStructuralLexicalizer({"coord_s" : "et"})
        res = l.entity_conjunction([n("NP", n("N", "Georges")), n("NP", n("N", "Marie")), n("NP", n("N", "Pierre"))])
        self.assertEqual(res.content["type"], "CP")
    
    def make_lexicalizer(self):
        relation_frames, argument_lexicon, tool_words, lexi = dummy_lexicon_en()
        s_l = SimpleBilingualStructuralLexicalizer(tool_words)
        e_l = TrivialEntityLexicalizer(argument_lexicon)
        r_l = TrivialRelationLexicalizer(relation_frames)
        return simple_lexicalizer(r_l, e_l, s_l, RotatingLexicon(lexi))
    
    def test_L_node(self):
        l = self.make_lexicalizer()
        res = l.lexicalize(DUMMY_RELATIONS[1])
        found = res.find(
            lambda x : x.content["type"] == "N" and  x.content["value"] == "programming", silent=True)
        self.assertEqual(found, n("N", u"programming"))
        res = l.lexicalize(DUMMY_RELATIONS[1])
        found = res.find(
            lambda x : x.content["type"] == "N" and  x.content["value"] == "programming2", silent=True)
        self.assertEqual(found, n("N", u"programming2"))
    
    def test_simple_lexicalizer(self):
        l = self.make_lexicalizer()
        res = l.lexicalize(DUMMY_RELATIONS[1])
        found = res.find(
            lambda x : x.content["type"] == "N" and  x.content["value"] == "programming", silent=True)
        self.assertEqual(found, n("N", "programming"))
    
    def test_aggregate(self):
        l = self.make_lexicalizer()
        aggregator = ConfiguredAggregator(testutils.make_conf_en())
        aggregate = aggregator.aggregate([DUMMY_RELATIONS[1], DUMMY_RELATIONS[2]])
        res = l.lexicalize(aggregate[0])
        vars = match(n("CP", n("C", "and"), var("a"), var("b")), res)
        self.assertTrue(vars)
        self.assertTrue("a" in vars)
        self.assertTrue("b" in vars)

if __name__ == '__main__':
    unittest.main()