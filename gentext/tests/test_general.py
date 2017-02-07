import unittest
from testutils import DUMMY_RELATIONS, make_conf_en, make_conf_fr, dummy_lexicon_en, dummy_lexicon_fr
from gentext.generator import *
from mock import MagicMock, Mock, call
from gentext.aggregator import *
from gentext.common import *
import functools
from gentext.lexicalizer import *
from gentext.loader import load_lexicalizer
import os

DUMMY_CONF = os.path.dirname(__file__) + '/letter_conf_test.json'

class TestLexicalUnit(unittest.TestCase):
    pass

class TestSentencePlanner(unittest.TestCase):
    pass

class TestAggregator(unittest.TestCase):
    pass

def default_write(aggregates):
    trees = []
    for aggregate in aggregates:
        children = []
        idx = 0
        for arg in aggregate.args :
            elems = []
            elem_idx = 0
            for elem in arg:
                elems.append(n('E-' + str(idx) + '-' + str(elem_idx), elem))
                elem_idx += 1
            children.append(n('LIST-' + str(idx), *elems))
            idx += 1
        trees.append(n("V", aggregate.name, *children))
    return trees

def default_writer():
    writer = Mock()
    writer.write = MagicMock(side_effect = lambda x : [n("S", "a")])

def dummy_planner(content_selector = None, aggregator = None, sentence_planner = None):
    if not content_selector :
        content_selector = Mock()
        content_selector.content_selection = MagicMock(return_value = DUMMY_RELATIONS)
    if not aggregator :
        aggregator = Mock()
        aggregator.aggregate = MagicMock(side_effect = lambda x : x)
    if not sentence_planner :
        sentence_planner = Mock()
        sentence_planner.plan = MagicMock(side_effect = lambda x : x)
    return FullMicroplanner(content_selector, aggregator, sentence_planner)

def dummy_generator(document_planner = None, writer = None, planner = None, write_fn = default_write):
        if not document_planner :
            document_planner = Mock()
            single_planner = None
            if planner :
                single_planner = planner
            else:
                single_planner = dummy_planner()
            document_planner.plan_document = MagicMock(side_effect = lambda x : [single_planner])
        if not writer :
            writer = Mock()
            writer.write = MagicMock(side_effect = write_fn)
        return TextGenerator(document_planner, writer)


class TestTopLevel(unittest.TestCase):
    
    def test_simple(self):
        mc = dummy_planner()
        a = mc.plan({})
        mc.aggregator.aggregate.assert_called_with(DUMMY_RELATIONS)
        mc.sentence_planner.plan.assert_called_with(DUMMY_RELATIONS)

    def test_microplan(self):
        gen = dummy_generator(write_fn = lambda x : [n("S", "a")])
        self.assertEqual(gen.generate({}),  [n("S", "a")])
        gen.document_planner.plan_document.assert_called_with({})
        gen.writer.write.assert_called_with(DUMMY_RELATIONS)
        
    def test_all(self):
        
        gen = dummy_generator()
        self.assertEqual(gen.generate({})[0].content["type"],"V")
        self.assertEqual(gen.generate({})[0].content["value"],"has_all_skills")
        gen.document_planner.plan_document.assert_called_with({})
        gen.writer.write.assert_called_with(DUMMY_RELATIONS)
    
class TestAggreg(unittest.TestCase):
    
    def test_simple(self):
        agg = ConfiguredAggregator(make_conf_en())
        res = agg.aggregate(DUMMY_RELATIONS)
        b = KnowledgeBase(res)
        self.assertTrue("has_skill_for_job" in b.facts)
        args = b.facts["has_skill_for_job"]
        self.assertEqual(len(args), 1)
        aggregated = args[0].args[0]
        self.assertEqual(len(aggregated), 4)
        self.assertTrue(all(map(lambda x : x in ["prog", "C#", "erlang", "java"], aggregated)))
    
    def test_simple2(self):
        agg = ConfiguredAggregator(make_conf_en())
        generator = dummy_generator(planner = dummy_planner(aggregator = agg))
        trees = generator.generate({})
        self.assertTrue(Fact("has_skill_for_job", {"prog", "C#", "erlang", "java"}))
        
    def test_joinable(self):
        facts = [Fact("x", [{"a", "b"}, {"a"}]), Fact("x", [{"a", "b"}, {"b"}])]
        self.assertEqual(joinable_idx(facts), 1)
        
        facts = [Fact("x", [{"a", "b"}, {"a"}]), Fact("x", [{"a", "b"}, {"b"}]), Fact("x", [{"a", "b"}, {"d"}])]
        self.assertEqual(joinable_idx(facts), 1)
        
        facts = [Fact("x", [{"a", "b"}, {"a"}]), Fact("x", [{"a", "b"}, {"b"}]), Fact("x", [{"a"}, {"d"}])]
        self.assertFalse(joinable_idx(facts))
        
        facts = [Fact("x", [{"a", "b"}, {"a"}]), Fact("x", [{"a", "b", "c"}, {"b"}])]
        self.assertFalse(facts[0].same_args(facts[1]))
        self.assertFalse(facts[0].same_arg(facts[1], 0))
        self.assertFalse(joinable_idx(facts))
    
class TestNucleiAggregator(unittest.TestCase):
    
    def test_simple(self):
        dummy_nuclei_conf = {
            "n1" : {
                "weight" : 1,
                "entity_weight_aversion" : 1,
                "juxtaposition_aversion" : 1,
                "relations":[{
                    "rel1" : 1.1,
                    "rel2" : 1.0
                    },
                    {
                    "rel1" : 1.0,
                    "rel2" : 1.1
                    }]
            }
                             }
        a = NucleiAggregator(dummy_nuclei_conf, ["n1"])
        nuclei = a.aggregate([Fact('rel1', ['1']), Fact('rel2', ['2'])])
        self.assertEqual(len(nuclei), 1)
        self.assertEqual(nuclei[0].name, 'n1')
        self.assertEqual(len(nuclei[0].args), 2) 
        
    def test_entity_aversion(self):
        dummy_nuclei_conf = {
            "n1" : {
                "weight" : 1,
                "entity_weight_aversion" : 0.75,
                "juxtaposition_aversion" : 1,
                "relations":[{"rel1" : 1, "rel2" : 1}]}}
        a = NucleiAggregator(dummy_nuclei_conf, ["n1"])
        nuclei = a.aggregate([Fact('rel2', ['1']), Fact('rel1', ['2', '3'])])
        self.assertEqual(len(nuclei), 1)
        self.assertEqual(nuclei[0].name, 'n1')
        self.assertEqual(len(nuclei[0].args), 1)
        
    
    def test_matching(self):
        dummy_nuclei_conf = {
            "n1" : {
                "weight" : 1,
                "entity_weight_aversion" : 1,
                "juxtaposition_aversion" : 1,
                "relations":[{"rel1" : 2,"rel2" : 1, "rel3" : 1, "rel4" : 1}]},
            "n2" : {
                "weight" : 1,
                "entity_weight_aversion" : 1,
                "juxtaposition_aversion" : 1,
                "relations":[{"rel1" : 1,"rel2" : 2, "rel3" : 1, "rel4" : 1},
                             {"non-existing-rel" : 1}]},
            "n3" : {
                "weight" : 1,
                "entity_weight_aversion" : 1,
                "juxtaposition_aversion" : 1,
                "relations":[{"rel1" : 1,"rel2" : 1, "rel3" : 2, "rel4" : 1, "rel5" : 1, "rel6" : 1}]},
                             
            "n4" : {
                "weight" : 1,
                "entity_weight_aversion" : 1,
                "juxtaposition_aversion" : 0.5,
                "relations":[{"rel1" : 1,"rel2" : 1, "rel3" : 1, "rel4" : 2, "rel5" : 1.95, "rel6" : 1}]},
                             
            "proof_same_name" : {
                "weight" : 1,
                "entity_weight_aversion" : 0.9,
                "juxtaposition_aversion" : 1,
                "relations":[{"rel6" : 1}]}
                }
        unmatched_fact = Fact('rel5', ['f5'])
        purged_fact = Fact('rel2', ['f2'])
        unmatched_fact_same_name1, unmatched_fact_same_name2 = Fact('rel6', ['f6']), Fact('rel6', ['f7'])
        facts = [Fact('rel1', ['f1']), purged_fact, Fact('rel3', ['f3']),
                 Fact('rel4', ['f4']), unmatched_fact,unmatched_fact_same_name1, unmatched_fact_same_name2]
        nuclei = ["n1", "n2", "n3", "n4", "proof_same_name"]
        matches, unmatched_nuclei_pos, unmatched_facts = match_nuclei_first_pass(facts, nuclei, dummy_nuclei_conf)
        self.assertTrue(('n2', 1) in unmatched_nuclei_pos)
        self.assertTrue(unmatched_fact in unmatched_facts)
        self.assertTrue(purged_fact not in unmatched_facts)
        
        matches, unmatched_facts, purged_nuclei = clean_unmatched_facts_and_nuclei(nuclei, matches, unmatched_nuclei_pos, unmatched_facts)
        self.assertEqual(['n1', 'n3', 'n4', 'proof_same_name'], purged_nuclei)
        self.assertTrue(unmatched_fact in unmatched_facts)
        self.assertTrue(purged_fact in unmatched_facts)
        
        nuclei_position_facts = match_nuclei_other_passes(matches, unmatched_facts, purged_nuclei, dummy_nuclei_conf)
        self.assertTrue(unmatched_fact in nuclei_position_facts[('n3', 0)])
        self.assertTrue(unmatched_fact not in nuclei_position_facts[('n4', 0)])
        self.assertTrue(unmatched_fact_same_name1 not in nuclei_position_facts[('n4', 0)])

        self.assertTrue(unmatched_fact_same_name1 in nuclei_position_facts[('proof_same_name', 0)])
        self.assertTrue(unmatched_fact_same_name2 in nuclei_position_facts[('proof_same_name', 0)])



def make_simple_lexicalizer():
    r, e, s, l = dummy_lexicon_en()
    relation_lexicalizer = TrivialRelationLexicalizer(r)
    entity_lexicalizer = TrivialEntityLexicalizer(e)
    structural_lexicalizer = SimpleBilingualStructuralLexicalizer(s)
    lex = RotatingLexicon(l)
    return simple_lexicalizer(relation_lexicalizer, entity_lexicalizer, structural_lexicalizer, lex)
        
class TestLexicon(unittest.TestCase):
    def test_simple(self):
        l = make_simple_lexicalizer()
        tree = l.lexicalize(Fact("has_skill_for_job", ['prog']))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "programming", silent = True))
        self.assertFalse(tree.find(lambda x: x.content["value"] == "java", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "I", silent = True))
        
    def test_aggregates_simple(self):
        l = make_simple_lexicalizer()
        tree = l.lexicalize(Fact("has_skill_for_job", [{'prog', 'java'}]))
        
        self.assertTrue(tree.find(lambda x: x.content["type"] == "C", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["type"] == "N", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "programming", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "Java", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "I", silent = True))

        conjunction = tree.find(lambda x: x.content["type"] == "CP", silent = True)
        self.assertTrue(conjunction)
        children = conjunction.children
        self.assertEqual([x.content["type"] for x in children], ["C", "N", "N"])
        self.assertEqual("and", children[0].content["value"])
        self.assertEqual("programming", children[1].content["value"])
        self.assertEqual("Java", children[2].content["value"])
        
    @unittest.skip("This was not implemented after some issues")
    def test_aggregates_with_preposition_repetition(self):
        l = make_simple_lexicalizer()
        tree = l.lexicalize(Fact("profile_skill_proficiency", [{'prog', 'java'}]))
        self.assertTrue(tree.find(lambda x: x.content["type"] == "C", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["type"] == "N", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "programming", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "Java", silent = True))
        self.assertTrue(tree.find(lambda x: x.content["value"] == "I", silent = True))
        conjunction = tree.find(lambda x: x.content["type"] == "CP", silent = True)
        self.assertTrue(conjunction)
        self.assertEqual([x.content["type"] for x in conjunction.children], ["C", "PP", "PP"])
        self.assertEqual([x.content["value"] for x in conjunction.leaves()], [u"and", u"in", u"programming", u"in", u"Java"])

class TestLoadAndBuild(unittest.TestCase):
    def test_load(self):
        r, e, s, m, l, nuclei_conf, nuclei_frames = load_lexicalizer(DUMMY_CONF)
        self.assertTrue("profile_skill_proficiency" in r)
        self.assertTrue("coord_s" in s)
        
    def test_simple_build(self):
        generator = build_generator(["hello"], DUMMY_CONF)
        self.assertEqual(generator.generate({}), [u'"hello"'])
        
    def test_simple_build2(self):
        class DummyContent(ContentSelector):
                def get_name(self):
                    return ""
                def content_selection(self, input_data):
                    return [Fact('profile_skill_proficiency', {'I', 'z_test1'})]
        class DummyMicro(Microplanner):
                def plan(self, input_data):
                    return [n("S", n("NP", n("N", "Johnny")), n("VP", n("V", "eat")))]
                
        sections = [
            lambda x : "This is a simple function {0}".format(x.items()),
            "This is some canned text",
            [Fact('profile_skill_proficiency', ['you', 'z_test1']),
             Fact('profile_skill_proficiency', ['you', 'z_test2']),
             Fact('profile_skill_expertise', ['I', 'z_test1'])
             ],
            DummyContent(),
            DummyMicro()
            ]
        generator = build_generator(sections, DUMMY_CONF)
        trees = generator.generate({1 : 2, "key" : "value"})
        self.assertEqual(trees[0], u"\"This is a simple function [(1, 2), (\\\'key\\\', \\\'value\\\')]\"")
        self.assertEqual(trees[1], u'"This is some canned text"')


if __name__ == '__main__':
    unittest.main()