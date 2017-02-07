from syntax import var, n, Node, TransformationRule, bind, match
from _collections import defaultdict

class RotatingLexicon():
    '''
    For each lexical entry, the rotating lexical has an associated circular list.
    '''
    def __init__(self, dic):
        self.dic = dic
        self.memory = defaultdict(lambda : 0)
        
    def __lexicalize(self, lexical_entry):
        if lexical_entry in self.dic:
            lexis = self.dic[lexical_entry]
            idx = self.memory[lexical_entry]
            lexi = lexis[idx]
            if idx == len(lexis) - 1:
                idx = 0
            else:
                idx = idx + 1
            self.memory[lexical_entry] = idx
            return lexi
        else :
            None
    
    def __setitem__(self, k, v):
            self.dic[k]= v
    
    def __contains__(self, lexical_entry):
        return lexical_entry in self.dic
        
    def __getitem__(self, lexical_entry):
        return self.__lexicalize(lexical_entry)

class Lexicalizer:
    '''
    Inheriting classes should handle the selection of  a relational frame for the aggregates,
    and delegate the lexicalization of entities to an entity lexicalizer. The entity lexicalizer
    is the one with referring expression awareness.
    '''
    def lexicalize(self, aggregate):
        raise NotImplementedError( "Should have implemented this" )

class EntityLexicalizer:
    '''
    Inheriting classes should handle the selection of a relational frame for the lexicon.
    '''
    def lexicalize(self, entity):
        raise NotImplementedError( "Should have implemented this" )

class StructuralLexicalizer:
    def entity_conjunction(self, with_prepositions):
        raise NotImplementedError("Should have implemented this")

    def clause_juxtaposition(self, facts):
        raise NotImplementedError("Should have implemented this")
    
    def clause_juxtaposition_same_subject(self, facts, repeated_subject=None, word = "coord_s"):
        raise NotImplementedError("Should have implemented this")


class RelationLexicalizer:
    def lexicalize(self, relation):
        raise NotImplementedError( "Should have implemented this" )

class OrthographicCorrecter():
    
    def verb_person(self, text_unit):
        try :
            subject_content = text_unit.children[0].children[0].content
            verb_content = text_unit.children[1].children[0].content
            if text_unit.content["type"] == "S" and subject_content["type"] == "Pro" and verb_content["type"] == "V" :
                verb_mods = verb_content["modifiers"]
                subject_mods = subject_content["modifiers"]
                if "pe" not in verb_mods and "pe" in subject_mods :
                    verb_mods["pe"] = subject_mods["pe"]
                if "n" not in verb_mods and "n" in subject_mods :
                    verb_mods["n"] = subject_mods["n"]
        except Exception :
            pass
        return text_unit
    
    def correct(self, text_unit):
        return self.verb_person(text_unit)

class PrimitiveLexicalizer():
    def __init__(self, relation_frames, argument_lexicon, tool_words, open_lexicon = True):
        self.open_lexicon = open_lexicon
        self.relation_frames = relation_frames
        self.argument_lexicon = argument_lexicon
        self.tool_words = tool_words
    
    def lexicalise_entity(self, e):
        try :
            return self.argument_lexicon[e]
        except KeyError as problem :
            if self.open_lexicon :
                return n("S", '${0}$'.format(e))
            else :
                raise problem
    
    def occurrence_lexicalisation(self, expr, var_name):
        new_var_parent = expr.parents(var_name)[0]
        occurrence_lexicalization = None
        if new_var_parent.content["type"] == "PP" :
            preposition = new_var_parent.children[0].content["value"]
            if new_var_parent.children[0].content["type"] == "P":
                occurrence_lexicalization = n("PP", n("P", preposition), var("x"))
        else :
            occurrence_lexicalization = var("x")
        return occurrence_lexicalization
    
    def modify_text_unit(self, text_unit, occurrence_lexicalisation, new_var):
        if occurrence_lexicalisation.is_var() :
            return text_unit
        if occurrence_lexicalisation.content["type"] == "PP" :
            preposition_node = occurrence_lexicalisation.children[0]
            preposition = preposition_node.content["value"]
            if preposition_node.content["type"] == "P":
                target_node = n("PP", n("P", preposition), var(new_var))
                replacement_node = var(new_var)
                return text_unit.replace_node(target_node, replacement_node) 
        return text_unit
    
    def enum(self, text_unit, idx, ordered_args, coord_word):
        new_vars, new_expression = text_unit.split_variable_occurrence(idx)
        for new_var in new_vars :
            occurrence_lexicalisation = self.occurrence_lexicalisation(new_expression, new_var)
            new_expression = self.modify_text_unit(new_expression, occurrence_lexicalisation, new_var)
            l = len(ordered_args)
            lexi = None
            if l == 0 :
                raise Exception('Empty argument!')
            elif l == 1 :
                lexi = occurrence_lexicalisation.replace("x", self.lexicalise_entity(ordered_args[0]))
            elif l > 1 :
                ls = []
                for i in xrange(len(ordered_args)) :
                    ls.append(occurrence_lexicalisation.replace("x", self.lexicalise_entity(ordered_args[i])))
                lexi = n("CP", n("C", self.tool_words['coord_s']), *ls)
            new_expression = new_expression.replace(new_var, lexi)
        return new_expression
    
    def extract_subject(self, text_unit):
        return text_unit.children[0], text_unit.children[1]
    
    def join_on_subject(self, text_unit1, text_unit2):
        s1, v1 = self.extract_subject(text_unit1)
        _, v2 = self.extract_subject(text_unit2)
        return n("S", s1, n("CP", n("C", self.tool_words["coord_s"]), v1, v2))
        
    
    def lexicalise(self, fact):
        text_unit = self.relation_frames[fact.name]
        for i in xrange(len(fact.args)):
            text_unit = self.enum(text_unit, i, [x for x in fact.args[i]], coord_word=self.tool_words["coord_s"])
        return text_unit

class SimpleBilingualStructuralLexicalizer(StructuralLexicalizer):
    def __init__(self, base_lexicon):
        self.base_lexicon = base_lexicon
        
        
    def clause_juxtaposition(self, trees, word = "coord_s"):
            return n("S", n("CP", self.base_lexicon[word], *trees))
        
    def clause_juxtaposition_same_subject(self, trees, repeated_subject=None, word = "coord_s"):
        subject = Node(content = {"type": "NP"}, children=[],var_name = "subject_phrase")
        verb = Node(content = {"type": "VP"}, children=[], var_name = "verb_phrase")
        simple_sentence_structure = n("S", subject, verb)
        verb_phrases = []
        subject = None
        for tree in trees:
            # And subject identification rules here.
            match = bind(simple_sentence_structure, tree)
            
            if not match :
                raise Exception('Could not match ' + tree)
            verb_phrases.append(match["verb_phrase"])
            if not subject :
                subject = match["subject_phrase"]
        if repeated_subject is None:
            clauses = [n("S", verb_phrase) for verb_phrase in verb_phrases[1:]]
            clauses = [trees[0]] + clauses
            return n("S", n("CP", self.base_lexicon[word], *clauses))
        else :
            clauses = [n("S", repeated_subject, verb_phrase) for verb_phrase in verb_phrases[1:]]
            clauses = [trees[0]] + clauses
            return n("S", n("CP", self.base_lexicon[word], *clauses))
    
    
    def entity_conjunction(self, entity_lexicalizations, word="coord_s", with_prepositions = False):
        return n("CP", self.base_lexicon[word], *entity_lexicalizations)
    
    def _entity_conjunction_with_preoposition(self, entity_lexicalizations, word="coord_s", with_prepositions = False):
        raise NotImplemented('This is not a priority')
    
    
class TrivialEntityLexicalizer(EntityLexicalizer):
    def __init__(self, entity_lexicon):
        self.entity_lexicon = entity_lexicon
        
    def lexicalize(self, entity):
        return self.entity_lexicon[entity]

class TrivialRelationLexicalizer:
    def __init__(self, frames):
        self.frames = frames
        
    def lexicalize(self, relation_name):
        return self.frames[relation_name]

def variable_generator(index):
    return 'X{0}'.format(index)

def default_entity_recovery(s):
    transformed = u" ".join([x.lower().capitalize() for x in s.split()])
    return n("NP", n("N", transformed))

class TopDownLexicalizer(Lexicalizer):
    
    def __init__(self, top_lexicalizer, bottom_lexicalizer, poly_arg_fn):
        self.bottom_lexicalizer = bottom_lexicalizer
        self.top_lexicalizer = top_lexicalizer
        self.poly_arg_fn = poly_arg_fn
    
    def _lexicalize_and_recovery(self, arg, recovery_fn = default_entity_recovery):
        bottom_lexicalized = self.bottom_lexicalizer.lexicalize(arg)
        if bottom_lexicalized is None:
            return recovery_fn(arg)
        return bottom_lexicalized
    
    def lexicalize(self, aggregate):
        frame = self.top_lexicalizer.lexicalize(aggregate.name)
        index = 0
        current_sentence = frame
        for aggregated_arguments in aggregate.args:
            lexicalized_aggregate_arguments = [self._lexicalize_and_recovery(arg) for arg in aggregated_arguments]
            lexicalized_argument = None
            if len(lexicalized_aggregate_arguments) == 1:
                lexicalized_argument = lexicalized_aggregate_arguments[0]
            elif len(lexicalized_aggregate_arguments) > 1:
                lexicalized_argument = self.poly_arg_fn(lexicalized_aggregate_arguments)
            else :
                raise Exception('Argument aggregate is empty for aggregate ' + str(aggregate) + " at position {0}".format(index + 1))
            if lexicalized_argument is None:
                raise Exception('Could not lexicalize argument position {0} for aggregate {1}'.format(str(index + 1), str(aggregate)))
            var_name = variable_generator(index + 1)
            current_sentence = current_sentence.replace(var_name, lexicalized_argument)
            index += 1
        return current_sentence
        

class TransformationLexicalizer(Lexicalizer):
    def __init__(self, lexicalizer, rules):
        self.rules = rules
        self.lexicalizer = lexicalizer
        
    def lexicalize(self, aggregate):
        current = self.lexicalizer.lexicalize(aggregate)
        for rule in self.rules:
            current = rule.replace_all(current)
        return current

def lexicalize_from_lexicon(lexicon, match):
        return lexicon[match.content["value"]]

def nuclei_lexicalizer(r_l, e_l, s_l, n_l, lexicon):
    relation_lexicalizer = TopDownLexicalizer(r_l, e_l, lambda x : s_l.entity_conjunction(x))
    top_lexicalizer =  TopDownLexicalizer(n_l, relation_lexicalizer, lambda x : s_l.clause_juxtaposition(x))
    matching_tree = var("relex")
    matching_tree.content = {"type" : 'L'}
    transformation_rule = matching_tree.copy()
    transformation_rule.content["transformation_fn"] = lambda x : lexicalize_from_lexicon(lexicon, x)
    relexicalize_rule = TransformationRule(matching_tree, transformation_rule)
    return TransformationLexicalizer(top_lexicalizer, [relexicalize_rule])


def simple_lexicalizer(r_l, e_l, s_l, lexicon):
    relation_lexicalizer = TopDownLexicalizer(r_l, e_l, lambda x : s_l.entity_conjunction(x))
    matching_tree = var("relex")
    matching_tree.content = {"type" : 'L'}
    transformation_rule = matching_tree.copy()
    transformation_rule.content["transformation_fn"] = lambda x : lexicalize_from_lexicon(lexicon, x)
    relexicalize_rule = TransformationRule(matching_tree, transformation_rule)
    return TransformationLexicalizer(relation_lexicalizer, [relexicalize_rule])

