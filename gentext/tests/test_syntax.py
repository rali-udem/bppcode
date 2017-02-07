import unittest

from gentext.syntax import n, var, TransformationRule, bind, print_jsrealb, CANNED_SYMBOL
from gentext.parse_syntax import *

class TestSyntax(unittest.TestCase):
    
    def test_split_var_occurrence_simple(self):
        new_vars, _ = n("S", var("1"), n("S2", var("1"))).split_variable_occurrence("1")
        for new_var in new_vars:
            self.assertTrue(new_var[0] == '@')
            
    def test_split_var_occurrence_no_split(self):
        new_vars, _ = n("S", var("1")).split_variable_occurrence("1")
        self.assertTrue(len(new_vars), 2)
        
    def test_replace_node(self):
        orig = n("S", n("S2", "a"), n("S1"))
        replaced = orig.replace_node(n("S2", "a"), n("S3", "b"))
        self.assertEqual(orig.children[0].content['value'], 'a')
        self.assertEqual(orig.children[0].content['type'], 'S2')
        
        self.assertEqual(replaced.children[0].content['value'], 'b')
        self.assertEqual(replaced.children[0].content['type'], 'S3')
        self.assertTrue(replaced)
        
    def test_find_all(self):
        e = n("S", n("S2", "a"), n("S1"))
        def has_type(x):
            try :
                if x.content['type']:
                    return True
            except:
                pass
            return False
        find_all = e.find_all(has_type)
        self.assertTrue(e in find_all)
        self.assertEqual(len(find_all), 3)
    
    def test_find(self):
        first_child = n("S2", "a")
        e = n("S", first_child, n("S1"))
        def has_type(x):
            try :
                if x.content['type']:
                    return True
            except:
                pass
            return False
        
        found = e.find(has_type)
        self.assertEqual(e, found)
        
        def has_type_s2(x):
            try :
                if x.content['type'] == 'S2':
                    return True
            except:
                pass
            return False
        
        found = e.find(has_type_s2)
        self.assertEqual(first_child, found)
        self.assertEqual(first_child, found)
        
        
    def test_var(self):
        orig = var("ok")
        replaced = orig.replace("ok", n("mixed"))
        self.assertEqual(orig.var_name, "ok")
        self.assertEqual(replaced.content['value'], "mixed")
    
    def test_shorthands(self):
        self.assertEqual(print_jsrealb(n("R", n("S", "gorgeous"), "mixed", var("var_name"), pe="2")),
                         'R(S("gorgeous"), "mixed", <var_name>).pe(2)')
        self.assertEqual(print_jsrealb(n("R", n("S", "gorgeous"), "mixed", var("var_name"), pe="2").replace(
            "var_name", n("F", "fr"))),
                         'R(S("gorgeous"), "mixed", F("fr")).pe(2)')


class TestInputSyntax(unittest.TestCase):
    
    def test_parse_quotes(self):
        raw_value = r"'normal text'"
        s = parse_quoted_text(raw_value)
        self.assertTrue(s.is_leaf())
        self.assertTrue(s.content["type"] == CANNED_SYMBOL)
        
        raw_value = r"'with an excaped quote \''"
        s = parse_quoted_text(raw_value)
        self.assertTrue(s.is_leaf())
        self.assertTrue(s.content["type"] == CANNED_SYMBOL)
        
        s = r'S(X1,X2)'
        tree = parse_node(s)
        
        self.assertFalse(tree.is_leaf())
        self.assertTrue(tree.content["type"] == "S")
        self.assertEqual([x.var_name for x in tree.leaves()], ["X1", "X2"])
        
        s = r'S(X1 ,X2)'
        tree = parse_node(s)
        
        self.assertFalse(tree.is_leaf())
        self.assertTrue(tree.content["type"] == "S")
        self.assertEqual([x.var_name for x in tree.leaves()], ["X1", "X2"])
        
        s = r'S(X1 ,S(X2))'
        tree = parse_node(s)
        
        s = r"S('ok', X92)"
        tree = parse_node(s)
        self.assertFalse(tree.is_leaf())
        self.assertTrue(tree.content["type"] == "S")
        self.assertEqual(["type" in x.content for x in tree.leaves()], [True, False])
        
        
        s = r"S(NP(Pro('I')), VP(V('be'), AP(A('strong'))))"
        tree = parse_node(s)
        self.assertFalse(tree.is_leaf())
        
    def test_notes(self):
        s = "'simple quote' [note=ok]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['note'], 'ok')
        
        s = "X1 [note=ok]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['note'], 'ok')
        
        s = "S(X1, X2) [note=ok]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['note'], 'ok')
        
        s = "N('ok1' [other_node1=embedded1], 'ok2'  [other_node2=embedded2]) [note=ok3]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['note'], 'ok3')
        self.assertEqual(tree.children[0].content['modifiers']['other_node1'], 'embedded1')
        self.assertEqual(tree.children[1].content['modifiers']['other_node2'], 'embedded2')
        
        

    
    
    def test_multiple_notes_on_node(self):
        s = u"N('Yes') [other_node1=embedded1; other_node12=embedded3]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['other_node1'], 'embedded1')
        self.assertEqual(tree.content['modifiers']['other_node12'], 'embedded3')
        
        s = u"V('be')[t=p; pe=3]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['t'], 'p')
        self.assertEqual(tree.content['modifiers']['pe'], '3')
        
        s = u"V('be')[t=p; pe=3]"
        tree = parse(s)
        self.assertEqual(tree.content['modifiers']['t'], 'p')
        self.assertEqual(tree.content['modifiers']['pe'], '3')
        
        s = u"N(V('1'), V('be')[t=p; pe=3])"
        tree = parse(s)
        self.assertEqual(tree.children[1].content['modifiers']['t'], 'p')
        self.assertEqual(tree.children[1].content['modifiers']['pe'], '3')
        
        s = u"VP(V('be') [t=p;pe=3], V('look') [t=pr], PP(P('for')))"
        tree = parse(s)
        self.assertEqual(tree.children[0].content['modifiers']['t'], 'p')
        self.assertEqual(tree.children[0].content['modifiers']['pe'], '3')
        
                
        s = u"WHICH_IS_ADV(X1, L('desire_phrase'), S(NP(D('my')[pe=1], N('client')), VP(V('be') [t=p;pe=3], V('look') [t=pr], PP(P('for')))))"
        tree = parse(s)
        self.assertEqual(tree.children[2].children[1].children[0].content['modifiers']['t'], 'p')
        self.assertEqual(tree.children[2].children[1].children[0].content['modifiers']['pe'], '3')
        
    def test_parse_rule(self):
        s = "S(X1, X2) => S(X2, X1)"
        rule = parse_rule(s)
        tree = parse("S('ax', 'bx')")
        self.assertEqual(rule.apply(tree), parse("S('bx', 'ax')"))
        
    def test_regex(self):
        self.assertEqual(re.findall(PATTERN_INT, ur'9')[0], ur'9')
        self.assertEqual(re.findall(PATTERN_EXPRESSION, ur'9')[0][0], ur'9')
        re.findall(PATTERN_EXPRESSION, ur'9,1')
        re.findall(exact(PATTERN_NODE)  + maybe(PATTERN_NOTE_LIST), ur"S('A')[12=12, lila= gr]")
        re.findall(PATTERN_ARGUMENT_LIST, ur'9,1')
        re.findall(PATTERN_NOTE_LIST, ur'[really=yeah, never=mind]')
        re.findall(PATTERN_EXPRESSION, ur'"ok"[really=yeah, never=mind2]')
        
        
class TestMatcher(unittest.TestCase):
    def test_simple_match(self):
        pattern = var("x")
        against = n("S", n("V", "ok"))
        bindings = bind(pattern, against)
        self.assertTrue("x" in bindings)
        self.assertTrue(bindings["x"] == n("S", n("V", "ok")))
        
    def test_deeper_match(self):
        
        pattern = n("S", var("x"))
        against = n("S", n("V", "ok"))
        bindings = bind(pattern, against)
        self.assertTrue("x" in bindings)
        self.assertTrue(bindings["x"] == n("V", "ok"))
        
    def test_impure_binding(self):
        
        impure_variable = n("V", "ok")
        impure_variable.var_name = "x"
        pattern = n("S", impure_variable)
        against = n("S", n("V", "ok"))
        bindings = bind(pattern, against)
        self.assertTrue("x" in bindings)
        self.assertTrue(bindings["x"] == n("V", "ok"))
        
    def test_two_vars(self):
        
        pattern = n("S", var("x"), var("y"))
        against = n("S", n("V", "should match x"), n("V", "should match y"))
        bindings = bind(pattern, against)
        self.assertTrue("x" in bindings)
        self.assertTrue(bindings["x"] == n("V", "should match x"))
        self.assertTrue(bindings["y"] == n("V", "should match y"))

    def test_embedded_var(self):
        
        impure_variable_inner = n("V", "will match")
        impure_variable_inner.var_name = "inner"
        
        impure_variable_outer = n("V", impure_variable_inner)
        impure_variable_outer.var_name = "outer"
        
        pattern = n("S", var("x"), impure_variable_outer)
        against = n("S", n("V", "should match x"), n("V", n("V", "won't match")))
        bindings = bind(pattern, against)
        self.assertFalse(bindings)
        
        against = n("S", n("V", "should match x"), n("V", n("V", "will match")))
        bindings = bind(pattern, against)
        self.assertTrue(bindings)
        self.assertTrue("inner" in bindings)
        self.assertTrue(bindings["inner"] == n("V", "will match"))
        
    def test_variable_conflict(self):
        pattern = n("S", var("x"), var("x"))
        against = n("S", n("V", "ok"), n("V", "ok"))
        bindings = bind(pattern, against)
        self.assertTrue(bindings)
        self.assertTrue("x" in bindings)
        
        pattern = n("S", var("x"), var("x"))
        against = n("S", n("V", "ok"), n("V", "okok"))
        bindings = bind(pattern, against)
        self.assertFalse(bindings)
        
        
    def test_variable_conflict2(self):
        pattern = n("S", var("x"), var("y"))
        against = n("S", n("V", "ok"), var("x"))
        bindings = bind(pattern, against)
        self.assertTrue(bindings)
        self.assertTrue("x" in bindings)
        self.assertTrue("y" in bindings)

        
        pattern = n("S", var("x"), var("x"))
        against = n("S", n("V", "ok"), n("V", "okok"))
        bindings = bind(pattern, against)
        self.assertFalse(bindings)
        
    
    def test_arguments(self):
        self.assertEqual(arguments("1, 2, 3"), [u'1', u' 2', u' 3'])
        self.assertEqual(arguments("NP(Pro('\I')), VP(V('be'), AP(A('strong')))"), [u"NP(Pro('\\I')), VP(V('be'), AP(A('strong')))"])
        
        
class TestTransformation(unittest.TestCase):
    def test_simple_transformations(self):
        commute_condition = n("+", var("x"), var("y"))
        commute_transformation = n("+", var("y"), var("x"))
        commute = TransformationRule(commute_condition, commute_transformation)
        
        res = commute.apply(n("+", n("1"), n("2")))
        self.assertEqual(res, n("+", n("2"), n("1")))
        
        associate_condition = n("+", n("+", var("x"), var("y")), var("z"),)
        associate_transformation = n("+", var("x"), n("+", var("y"), var("z")))
        associate = TransformationRule(associate_condition, associate_transformation)

        res = associate.apply(n("+", n("+", n("1"), n("2")), n("3")))
        self.assertEqual(res, n("+", n("1"), n("+", n("2"), n("3"))))
        
    def test_transformation_fns(self):
        def some_fn(node_input):
            return n("+", node_input.content["value"], "0")
        cdn = var("x")
        transformation_node = var("x")
        transformation_node.content["transformation_fn"] = some_fn
        t = TransformationRule(cdn, transformation_node)
        res = t.apply(n("1"))
        self.assertEqual(res, n("+", n("1"), n("0")))
        
    def test_match(self):
        commute_condition = n("+", var("x"), var("y"))
        commute_transformation = n("+", var("y"), var("x"))
        commute = TransformationRule(commute_condition, commute_transformation)
        
        res = commute.replace_once(n("&", n("a"), n("+", n("1"), n("2"))))
        self.assertEqual(res, n("&", n("a"), n("+", n("2"), n("1"))))

if __name__ == '__main__':
    unittest.main()