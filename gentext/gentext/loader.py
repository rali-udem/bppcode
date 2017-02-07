
import json
import parse_syntax
from lexicalizer import RotatingLexicon
import random

def parse(x):
    try:
        return parse_syntax.parse(x)
    except Exception as e:
        print x
        failed_str = 'Could not parse "{0}".'.format(x)
        raise Exception('{0}\\n{1}'.format(failed_str, e))
    
def parse_rule(x):
    try:
        return parse_syntax.parse_rule(x)
    except Exception as e:
        print x
        failed_str = 'Could not parse rule "{0}".'.format(x)
        raise Exception('{0}\\n{1}'.format(failed_str, e))
    

def shuffle(ls):
    random.shuffle(ls)
    return ls
def apply_shorthands(shorthands, x):
    for shorthand in shorthands:
        x = shorthand.replace_all(x)
    return x


def load_lexicalizer(filename):
    with open(filename) as f :
        content = f.read()
        as_dic = json.loads(content)
        try :
            shorthands = [parse_rule(x) for x in as_dic['shorthands']]
        except KeyError :
            shorthands = []
        
    def parse_with_sh(x):
        return [apply_shorthands(shorthands, parse(y)) for y in x]
    relation_frames = RotatingLexicon({relation_name: shuffle(parse_with_sh(relation_details["frames"])) 
                                       for relation_name, relation_details in as_dic["relations"].iteritems()})
    entities = {entity_id: shuffle(parse_with_sh(details["lexi"]))
                for entity_id, details in as_dic["entities"].iteritems()}
    hardcoded_entities = {entity_id: shuffle(parse_with_sh(details["lexi"]))
                          for entity_id, details in as_dic["hardcoded_entities"].iteritems()}
    entities.update(hardcoded_entities)
    entities = RotatingLexicon(entities)
    
    structure_words = RotatingLexicon({entity_id: shuffle(parse_with_sh(details["lexi"]))
                                       for entity_id, details in as_dic["structure"]["words"].iteritems()})
    nuclei_conf = as_dic["nuclei_conf"]
    nuclei_frames = RotatingLexicon({entity_id: shuffle(parse_with_sh(details["frames"]))
                                     for entity_id, details in nuclei_conf["nuclei"].iteritems()})
    lexicon = RotatingLexicon({lexical_entry: shuffle(parse_with_sh(details["lexi"]))
                               for lexical_entry, details in as_dic["lexicon"].iteritems()})
    try :
        mods = {entity_id: shuffle(parse_with_sh(details["lexi"]))
                for entity_id, details in as_dic["structure"]["mods"].iteritems()}
    except KeyError :
        mods = {}
    return relation_frames, entities, structure_words, mods, lexicon, nuclei_conf, nuclei_frames