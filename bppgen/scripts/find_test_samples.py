from bppgen.letter.letter import build_data_insight, build_letter_generator
from bppgen.data.mongoaccess import BppMongoDataSource
from collections import Counter
import json, copy, io, html
from bppgen.api.profile_api import BPPAPI
from bson.objectid import ObjectId

def clear_object_id(o):
    if isinstance(o, list):
        return [clear_object_id(elem) for elem in o]
    elif isinstance(o, dict):
        return {k: clear_object_id(v) for k, v in o.iteritems()}
    elif isinstance(o, ObjectId):
        return str(o)
    return o

def find_interesting_letter(profiles_fn, offers, lang, min_kinds_of_facts):
    di = build_data_insight(lang)
    matched_o = set()
    matched_p = set()
    c = Counter()

    matched_profiles = set()
    pairs = []
    fails = 0
    for o in offers:
        try:
            best = 0
            best_p = None
            best_facts = None
            best_kinds_of_facts = 0
            
            for p in profiles_fn(o):
                if str(p["_id"]) in matched_profiles:
                    continue
                facts = di.content_selection(
                        {'offer' : o, 'candidate' : p})
                kinds_of_facts = {}
                for fact in facts:
                    kinds_of_facts[fact.name] = 1
                kinds_of_facts = len(kinds_of_facts)
                
                if kinds_of_facts > best_kinds_of_facts :
                    best_p = p
                    best_facts = facts
                    best_kinds_of_facts = kinds_of_facts
                    
            if best_p and best_kinds_of_facts >= min_kinds_of_facts :
                c[best] += 1
                ids = str(best_p["_id"])
                matched_profiles.add(ids)
                c_p = copy.deepcopy(best_p)
                c_p["_id"] = ids
                o_p = copy.deepcopy(o)
                o_p["_id"] = str(o["_id"])
                pairs.append({"offer": o_p, "candidate" : c_p, "kinds_of_facts" : best_kinds_of_facts,
                              "facts" : [str(x) for x in best_facts]})
        except :
            fails += 1
            if fails > len(offers) / float(10) :
                raise Exception('Too many errors')
    print len(pairs)
    
    with open('test_examples_' + lang + '.json', mode='w+') as f:
        f.write(json.dumps(clear_object_id(pairs), f, indent=4).encode('utf-8'))


def exhaustive_search(lang, limit, min_kinds_of_facts):
    q_p = {'langid' : lang, 'precalc.skills.4' : {'$exists': True}, 'precalc.experiences.4' : {'$exists': True}}
    q_o = {'langid' : lang, '$where': "this.description.length > 1000"}
    ds = BppMongoDataSource()
    profiles = [x for x in ds.mongo_access.db['profiles'].find(q_p).limit(limit)]
    offers = [x for x in ds.mongo_access.db['offers'].find(q_o).limit(limit)]
    return find_interesting_letter(lambda x: profiles, offers, lang, min_kinds_of_facts)


def gen_many_copies(lang, id, num_copies):
    pair = None
    with open('test_examples_' + lang + '.json') as f:
        pair = json.loads(f.read().decode('utf-8'))[id]
    generator = build_letter_generator(lang)
    DEMO_MODE = True
    htmler = HTMLGenerator(lang)
    pair['generation_data'] = {"lang" :lang, "formality" : 1, "psy" :u"I"}
    datas = []
    for i in xrange(num_copies):
        with open('/u/grandmph/bppgen/static/copy_' + str(id) + '_' + str(i) + '.html', mode='w+') as f:
            s = htmler.generate(generator.generate(pair), datas = {"Offer" : pair['offer'], "Profile" : pair["candidate"]})
            f.write(s.encode('utf-8'))

def gen_letter(lang):
    pairs = None
    with open('test_examples_' + lang + '.json') as f:
        pairs = json.loads(f.read().decode('utf-8'))
    generator = build_letter_generator(lang)
    DEMO_MODE = True
    htmler = HTMLGenerator(lang)
    idx = 1
    for pair in pairs:
        pair['generation_data'] = {"lang" : lang, "formality" : 1, "psy" :u"I"}
        generated = generator.generate(pair)
        datas = []
        with open('/u/grandmph/bppgen/static/letter_' + lang + '_' + str(idx) + '.html', mode='w+') as f:
            s = htmler.generate(generated, datas = {"Offer" : pair['offer'], "Profile" : pair["candidate"]})
            f.write(s.encode('utf-8'))
        idx += 1
def write_html(generated_text):
    pass

if __name__ == '__main__':
    #exhaustive_search('en', 400, 5)
    #gen_many_copies('en', 10, 10)
    pass
    