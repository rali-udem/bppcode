from _collections import defaultdict
from common import Fact, Nucleus

class KnowledgeBase():
    '''
    This class simply indexes relations for easier manipulation. It is nothing like a KB.
    '''
    def __init__(self, relations):
        self.facts = defaultdict(list)
        self.entity_idx = defaultdict(list)
        self.entities = set()
        for relation in relations :
            self.facts[relation.name].append(relation)
            for arg_enumeration in relation.args :
                for arg in arg_enumeration :
                    self.entity_idx[arg].append(relation)
                    self.entities.add(arg)
    
    def is_singular(self):
        for facts in self.facts.itervalues():
            for fact in facts:
                for child_aggregate in fact.children:
                    if len(child_aggregate) != 1:
                        return False
        return True
            
    def __str__(self):
        return str(type(self)) + str(dict((name, getattr(self, name)) for name in dir(self) if not name.startswith('__')))
    
    def __iter__(self):
        return [fact for fact in reduce(lambda x, y : x + y, self.facts.values())].__iter__()
    
    
    def aggregate(self, rel_name, idx = None):
        s = set()
        first_fact = None
        for fact in self.facts[rel_name]:
            if not first_fact :
                first_fact = fact
            s = s.union(fact.args[idx])
        
        new_args = [x for x in first_fact.args]
        new_args[idx] = s
        return Fact(rel_name, new_args)

### HELPER FUNCTIONS ####
def joinable_idx(facts):
    arity = len(facts[0].args)
    for i in xrange(arity):
        fail = False
        # We only look to join things that are already different
        if all([facts[0].same_arg(x, i) for x in facts[1:]]):
            continue
        
        # For all other arguments, they must be the same
        for j in xrange(arity):
            if i == j :
                continue
            if not all([facts[0].same_arg(x, j) for x in facts[1:]]):
                fail = True
                break
        if not fail:
            return i
    return None
# For all argument position, look if the other arguments are the same
def _find_any_idx(base, rel_name):
    facts = base.facts[rel_name]
    if len(facts) > 1:
        return joinable_idx(facts)
    else :
        return None

def idx_from_conf(base, rel_name, conf):
    param_aggregations_idx = conf["param_aggregations"]
    if rel_name in param_aggregations_idx :
            return param_aggregations_idx[rel_name]
    else :
        return None

class ConfiguredAggregator():
    def __init__(self, conf = None, join_fn = None):
        if conf and not join_fn :
            self.join_fn = lambda x, y : idx_from_conf(x, y, conf)
        elif not join_fn :
            self.join_fn = _find_any_idx
        else :
            self.join_fn = join_fn
    
    def aggregate(self, relations):
        if isinstance(relations, KnowledgeBase):
            base = relations
        else:
            base = KnowledgeBase(relations)
        ls = []
        for rel_name in base.facts :
            join_index = self.join_fn(base, rel_name)
            if join_index is None :
                ls += base.facts[rel_name]
            else :
                ls.append(base.aggregate(rel_name, join_index))
        return ls

def all_scores(men, women, calc_score):
    all_pairs = []
    
    for man in men:
        for woman in women:
            score = calc_score(man, woman)
            
            if score is not None:
                all_pairs.append((man, woman, calc_score(man, woman)))
    all_pairs.sort(key=lambda x: x[2], reverse=True)
    return all_pairs
    
def matching(men, women, calc_score):
    all_pairs = all_scores(men, women, calc_score)
    
    first_pass_matching = {}
    unmatched_women = set(women)
    for man, woman, _ in all_pairs:
        if man not in first_pass_matching and woman in unmatched_women:
            first_pass_matching[man] = woman
            unmatched_women.remove(woman)
    unmatched_men = set([x for x in men if x not in first_pass_matching])
    return first_pass_matching, unmatched_men, unmatched_women


def match_nuclei_first_pass(base, nuclei, nuclei_conf):
    nuclei_positions = []
    for nucleus in nuclei:
        nucleus_conf = nuclei_conf[nucleus]
        positions = range(len(nucleus_conf["relations"]))
        for position in positions:
            nuclei_positions.append((nucleus, position))
    
    def first_pass_score_fn(nucleus_pos, fact):
        nucleus, pos = nucleus_pos
        conf = nuclei_conf[nucleus]["relations"][pos]
        name = fact.name
        if name not in conf:
            return None
        else:
            return conf[name]
    first_pass = matching(nuclei_positions, [x for x in base], first_pass_score_fn)
    return first_pass

def clean_unmatched_facts_and_nuclei(nuclei, matches, unmatched_nuclei_pos, unmatched_facts):
    incomplete_nuclei = set([x for x, _ in unmatched_nuclei_pos])
    new_matches = {}
    new_unmatched_facts = set(unmatched_facts)
    for nuclei_pos, fact in [x for x in matches.items()]:
        if nuclei_pos[0] in incomplete_nuclei:
            new_unmatched_facts.add(fact)
        else:
            new_matches[nuclei_pos] = fact
    new_nuclei = [x for x in nuclei if not x in incomplete_nuclei]
    return new_matches, new_unmatched_facts, new_nuclei


def match_nuclei_other_passes(matches, unmatched_facts, purged_nuclei, nuclei_conf):
    dico = defaultdict(set)
    nuclei_positions = []
    for nucleus in purged_nuclei:
        nucleus_conf = nuclei_conf[nucleus]
        positions = range(len(nucleus_conf["relations"]))
        for position in positions:
            nuclei_positions.append((nucleus, position))
            dico[(nucleus, position)].add(matches[(nucleus, position)])
    def other_pass_fn(nuclei_pos, fact):
        nucleus, pos = nuclei_pos
        conf = nuclei_conf[nucleus]
        aversion = conf["juxtaposition_aversion"]
        rel = conf["relations"][pos]
        name = fact.name
        if name not in rel:
            return None
        else:
            current_facts = dico[(nucleus, position)]
            names = set([x.name for x in current_facts])
            same_relation_bonus = 1
            if fact.name in names:
                same_relation_bonus = 2
            number_of_facts = len(current_facts)
            juxtaposition_modifier = aversion ** number_of_facts
            return rel[name] * juxtaposition_modifier * same_relation_bonus
    change = True
    while change:
        scores = all_scores(nuclei_positions, unmatched_facts, other_pass_fn)
        if scores:
            nucleus_pos, fact, _ = scores[0]
            dico[nucleus_pos].add(fact)
            unmatched_facts.remove(fact)
        else:
            change = False
    return dico


def match_nuclei(base, nuclei, nuclei_conf):
    matches, unmatched_nuclei_pos, unmatched_facts = match_nuclei_first_pass([x for x in base], nuclei, nuclei_conf)
    matches, unmatched_facts, purged_nuclei = clean_unmatched_facts_and_nuclei(nuclei, matches,
            unmatched_nuclei_pos, unmatched_facts)
    return match_nuclei_other_passes(matches, unmatched_facts, purged_nuclei, nuclei_conf)
                     

class NucleiAggregator():
    def __init__(self, nuclei_conf, nuclei_order):
        self.configured_aggregator = ConfiguredAggregator()
        self.nuclei_conf = nuclei_conf
        self.nuclei_order = nuclei_order
    
    def aggregate(self, facts):
        dico = match_nuclei(facts, self.nuclei_order, self.nuclei_conf)
        with_agregations = defaultdict(set)
        for nucleus_pos, current_facts in dico.iteritems():
            agregated_facts = {}
            for fact in current_facts:
                name = fact.name
                if name not in agregated_facts:
                    agregated_facts[name] = fact
                else:
                    current_aggregate = agregated_facts[name]
                    merged_aggregate = current_aggregate.merge(fact)
                    if merged_aggregate:
                        agregated_facts[name] = merged_aggregate
            with_agregations[nucleus_pos] = set(agregated_facts.values())
        
        nuclei_list = []
        complete_nuclei = set([x for x, _ in with_agregations])
        for nucleus in self.nuclei_order:
            if nucleus in complete_nuclei:
                args = []
                idx = 0
                while True:
                    k = (nucleus, idx)
                    if k in with_agregations:
                        args.append(with_agregations[k])
                        idx += 1
                    else:
                        break
                nuclei_list.append(Nucleus(nucleus, args))
        return nuclei_list
