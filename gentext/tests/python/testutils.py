#!/usr/bin/env python
# coding=utf-8
from gentext.common import Fact
from gentext.syntax import n, var, canned
import os
import json

NEW_LEXICON = json.dumps({"what": {
        "Pro": {
            "tab": ["pn7","pn6"]
        }
    },
    "that": {
        "Pro": {
        "tab": ["pn7","pn6"]
    }
    },
    "although": {
        "Adv": {
        "tab": ["b1"]}
    },
    "as" : {
    "P": {
        "tab": ["pp"]}
    },
    "required" : {
    "A": {
     "tab": ["a1"]}
    }
})

class Dummy():
    pass

def test_offer():
    with open(os.path.dirname(__file__) + '/test_data/test_offer') as f :
        return json.load(f)
    
def test_candidate():
    with open(os.path.dirname(__file__) + '/test_data/test_candidate') as f :
        return json.load(f)

DUMMY_RELATIONS = [
        Fact('has_all_skills', []),
        Fact("has_skill_for_job", ['prog']),
        Fact("has_skill_for_job", ['erlang']),
        Fact("has_skill_for_job", ['java']),
        Fact("has_skill_for_job", ['C#']),
        Fact("expert_in", ['prog']),
        Fact("expert_in", ['java']),
        Fact("expert_in", ['erlang'])]



def dummy_lexicon_en():
    address = n("SP", n("Pro", u"I", pe = 2))

    
    tool_words = {
                "coord_s" : n("C", "and")
                }
    
    relation_frames = {
                    "has_all_skills" : n("S", address,
                                    n("VP", n("V", u"have", t = "p"),
                                    n("NP", canned(u"all the skills required for the job.")))),
                    "has_skill_for_job" : n("S", address, n("VP", n("V", u"have", t = "p"),
                                        n("NP", canned(u"the essential skills for the job (namely "),
                                        var("X1"), canned(u").")))),
                    "expert_in" : n("S", address,
                                    n("VP", n("V", u"be", t = "p"),
                                    n("AP", n("A", u"expert"), n("PP", n("P", u"in"), var("X1")))))
                    }
    argument_lexicon = {
                    "you" : address,
                    "job" : n("NP", n("N", u"agent")),
                    "prog" : n("L", u"programming"),
                    "java" : n("N", u"Java"),
                    "erlang" : n("N", u"Erlang"),
                    "C#" : n("N", u"C#")
                    }
    
    lexi = {
        u"programming" : [n("N", "programming"), n("N", "programming2")]
        }
    
    return relation_frames, argument_lexicon, tool_words, lexi

def dummy_lexicon_fr():
        
    address = n("SP", n("Pro", u"je", pe = 2, n = "p"))
    
    tool_words = {
                "coord_s" :  n("C", "and")
                }
    
    relation_frames = {
                    "has_all_skills" : n("S", address,
                                    n("VP", n("V", u"avoir", t = "p"),
                                    n("NP", canned(u"toutes les compétences exigées pour cette offre")))),
                    "has_skill_for_job" : n("S", address, n("VP", n("V", u"avoir", t = "p"),
                                        n("NP", canned(u"une compétence essentielle ("),
                                        var(0), canned(u") pour l'offre.")))),
                    "expert_in" : n("S", address,
                                    n("VP", n("V", u"être", t = "p"),
                                    n("AP", n("A", u"expert"), n("PP", n("P", u"en"), var(0)))))
                    }
    argument_lexicon = {
                    "tu" : n("SP", n("Pro", u"je", pe = 2)),
                    "vous" : address,
                    "job" : n("NP", n("N", u"agent"), canned(u"de bord")),
                    "prog" : n("NP", n("N", u"programmation")),
                    "java" : n("NP", n("N", u"Java")),
                    "erlang" : n("NP", n("N", u"Erlang")),
                    "C#" : n("NP", n("N", u"C#"))
                    }
    
    return tool_words, relation_frames, argument_lexicon




def make_conf_fr(formal = True):
    address = "vous" if formal else "tu"
    conf_variables = {
            "address" : address
    }
    canned_phrases = {
            }
    return {
        "conf_variables" : conf_variables,
        "phrases" : canned_phrases,
        "param_aggregations" : {
                            "expert_in" : 0,
                            "has_skill_for_job" : 0
            }}
    
def make_conf_en(formal = True):
    conf_variables = {
            "address" : "you"
        }
    canned_phrases = {
            }
    return {
        "conf_variables" : conf_variables,
        "phrases" : canned_phrases,
        "param_aggregations" : {
                            "expert_in" : 0,
                            "has_skill_for_job" : 0
                            }
        }
