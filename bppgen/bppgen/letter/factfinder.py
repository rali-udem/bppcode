## This module creates the facts that are going to be expressed in the letter.

import os, pickle, copy, json
from collections import defaultdict, Counter

def invert(dic):
    inverted = defaultdict(list)
    for k, v in dic.iteritems():
        for item in v:
            inverted[item].append(k)
    return inverted

class FactFinder():
    
    def __init__(self, skill_implies_skill, skill_implies_occupation, occupation_implies_skill, occupation_implies_occupation,
                 occupation_is_more_junior, occupation_is_more_senior, occupation_is_similar_to):
        
        self.skill_implies_skill = skill_implies_skill
        self.skill_implies_occupation = skill_implies_occupation
        
        self.occupation_implies_skill = occupation_implies_skill
        self.occupation_implies_occupation = occupation_implies_occupation
        
        self.occupation_is_more_junior = occupation_is_more_junior
        self.occupation_is_more_senior = occupation_is_more_senior
        self.occupation_is_similar_to = occupation_is_similar_to
        
        self.skill_implied_by_skill = invert(self.skill_implies_skill)
        self.skill_implied_by_occupation = invert(self.occupation_implies_skill)
        self.occupation_implied_by_skill = invert(self.skill_implies_occupation)
    
    def describe_skill(self, skill_id):
        return {
            "implied_occupations" : self.skill_implies_occupation[skill_id],
            "implied_skills" : self.skill_implies_skill[skill_id],
            "skills_implying" :self.skill_implied_by_skill[skill_id],
            "occupations_implying" :self.skill_implied_by_occupation[skill_id],

            }
        
    def describe_occupation(self, occupation_id):
        return {
            "implied_skills" : self.occupation_implies_skill[occupation_id],
            "implied_occupation" : self.occupation_implies_occupation[occupation_id],
            "junior" : self.occupation_is_more_junior[occupation_id],
            "senior" :self.occupation_is_more_senior[occupation_id],
            "similar" : self.occupation_is_similar_to[occupation_id],
            "occupations_implying" :self.occupation_implied_by_skill[occupation_id]
            }

def iter_ordered(dic):
        keys = dic.keys()
        for k in sorted(keys, reverse = True):
            yield k, dic[k]


def load_dic(filename):
    with open(filename) as f:
        return json.load(f)

def load_lists(dic, mini, maxi):
    if mini is None:
        mini = -1
    if maxi is None:
        maxi = 2
    for k, v in iter_ordered(dic):
        k = float(k)
        if k >= mini and k <= maxi :
            for t in v:
                yield t

def remove_all(origin, filtered):
   return [value for value in origin if value not in filtered]

class FactFinderBuilder():
    def __init__(self, lang, mini = None, maxi = None):
        self.lang = lang
        prefix = '{1}/letter_data/{0}/'.format(self.lang, os.path.dirname(__file__))
        
        
        self.skill_occu = [x for x in load_lists(load_dic('{0}cond_both'.format(prefix)), 0.1, maxi)]
        self.skills = [x for x in load_lists(load_dic('{0}cond_skills'.format(prefix)), 0.1, maxi)]
        self.occus = [x for x in load_lists(load_dic('{0}cond_occus'.format(prefix)), 0.1, maxi)]
        self.occu_orders = [x for x in load_lists(load_dic('{0}occupation_orders'.format(prefix)), mini, maxi)]

    def build_dics(self):
        skill_implies_skill = defaultdict(set)
        occupation_implies_skill = defaultdict(set)
        skill_implies_occupation = defaultdict(set)
        occupation_implies_occupation = defaultdict(set)
        occupation_is_more_junior = defaultdict(set)
        occupation_is_more_senior = defaultdict(set)
        
        for prior, posterior, power, count in self.skill_occu:
            norm_prior = prior[2:]
            norm_posterior = posterior[2:]
            
            if prior[0] == u's':
                occupation_implies_skill[norm_posterior].add((norm_prior, power))
            elif prior[0] == u'o':
                skill_implies_occupation[norm_posterior].add((norm_prior, power))
        
        for prior, posterior, power, count in self.skills:
            skill_implies_skill[posterior].add((prior, power))
            
        for prior,posterior, power, count in self.occus:
            occupation_implies_occupation[posterior].add((prior, power))
        
        for prior, posterior, power, count in self.occu_orders:
            norm_prior = prior[2:]
            norm_posterior = posterior[2:]
            
            if prior[0] == u'b':
                occupation_is_more_junior[norm_posterior].add((norm_prior, power))
            elif prior[0] == u'a':
                occupation_is_more_senior[norm_posterior].add((norm_prior, power))
                
        occupation_implies_skill = self.keep_best(occupation_implies_skill)
        skill_implies_occupation = self.keep_best(skill_implies_occupation, min_rate=0.6)
        occupation_implies_occupation = self.keep_best(occupation_implies_occupation, min_rate=0.5)
        skill_implies_skill = self.keep_best(skill_implies_skill, min_rate=0.5)
        occupation_is_more_senior = self.keep_best(occupation_is_more_senior)
        occupation_is_more_junior = self.keep_best(occupation_is_more_junior)
                
        occupation_is_similar_to = self.similar_occupations(occupation_is_more_junior, occupation_is_more_senior)
        
        
        return (skill_implies_skill, skill_implies_occupation, occupation_implies_skill,
                          occupation_implies_occupation, occupation_is_more_junior,
                          occupation_is_more_senior, occupation_is_similar_to)

    def build(self):
        d = self.build_dics()
        return FactFinder(*d)

    def keep_best(self, dict_of_sets, threshold = 20, max_gap = 1, min_rate = 0):
        dic = defaultdict(list)
        
        for k, v in dict_of_sets.iteritems():
            last = None
            ls = []
            for val, proba in sorted(v, key=lambda x : x[1], reverse=True):
                if last is None:
                    last = proba
                elif proba < min_rate :
                    break
                elif last - proba > max_gap:
                    break
                elif len(ls) >= threshold:
                    break
                else:
                    ls.append(val)
            if ls:
                dic[k] = ls
                
        return dic
                
    def similar_occupations(self, occupation_is_more_junior, occupation_is_more_senior):
        occupation_is_similar_to = defaultdict(set)
        this_copy = [(x, copy.deepcopy(y)) for x, y in occupation_is_more_junior.iteritems()]
        for k, v in this_copy :
            for other in v :
                if k in occupation_is_more_junior[other] :
                    occupation_is_similar_to[other].add(k)
                    occupation_is_similar_to[k].add(other)
                    
        this_copy = [(x, copy.deepcopy(y)) for x, y in occupation_is_more_senior.iteritems()]
        for k, v in this_copy :
            for other in v :
                if k in occupation_is_more_senior[other] :
                    occupation_is_similar_to[other].add(k)
                    occupation_is_similar_to[k].add(other)
        
        for k, v in occupation_is_similar_to.iteritems():
            if k in occupation_is_more_senior:
                occupation_is_more_senior[k] = remove_all(occupation_is_more_senior[k], v)
            if k in occupation_is_more_junior:
                occupation_is_more_junior[k] = remove_all(occupation_is_more_junior[k], v)
        
        return occupation_is_similar_to

        
    def facts_about_skill_and_occupation(self, skill_occupation, skill_occus):
        pass
    
    def skill_is_implied_by_occupation(self, ):
        pass
    

def inspect_occupations(lang):
    fact_finder = FactFinderBuilder(lang).build()
    with_skills = 0
    senior = 0
    junior = 0
    interesting = 0
    for line in open(os.path.dirname(__file__) + '/letter_data/' + lang + '/lexicon_job'):
        splitted = line.split(',')
        if len(splitted) == 2:
            description = fact_finder.describe_occupation(splitted[0])
            show = False
            if len(description['implied_skills']):
                show = True
                with_skills += 1
            if len(description['senior']):
                senior += 1
                show = True
            if len(description['junior']):
                junior += 1
                show = True
            if show:
                interesting += 1
                print splitted[0], description
                
    print 'skills:', with_skills
    print 'senior:', senior
    print 'junior:', junior
    print 'interesting:', interesting
    
    return fact_finder


def inspect_skills(lang):
    fact_finder = FactFinderBuilder(lang).build()
    with_skills = 0
    with_occupations = 0
    interesting = 0
    c_skills = Counter()
    c_occupations = {}
    
    for line in open(os.path.dirname(__file__) + '/letter_data/' +  lang + '/lexicon_skill'):
        splitted = line.split(',')
        if len(splitted) == 2:
            description = fact_finder.describe_skill(splitted[0])
            show = False
            if len(description['implied_skills']):
                show = True
                with_skills += 1
                c_skills[splitted[0]] = len(description['implied_skills'])
                    
            if len(description['implied_occupations']):
                with_occupations += 1
                show = True
            if show:
                interesting += 1
                print splitted[0], description
                
    print c_skills.most_common(30)
    print 'with_occupations:', with_occupations
    print 'with_skills:', with_skills
    print 'interesting:', interesting
    
    return fact_finder

def most_interesting(lang, n, job):
    builder = FactFinderBuilder(lang)
    (skill_implies_skill, skill_implies_occupation, occupation_implies_skill,
                          occupation_implies_occupation, occupation_is_more_junior,
                          occupation_is_more_senior, occupation_is_similar_to) = builder.build_dics()
    print occupation_implies_skill[job]


def count_counter(cnt):
    accu = 0
    for k, v in cnt.iteritems():
        accu += k * v
    return accu
    

def inspect_assocs(assocs, peek_value, peek_max = 10):
    cntr = Counter()
    peeks = 0
    for k, v in assocs.iteritems():
        l = len(v)
        cntr[l] += 1
        if l > peek_value and peeks < peek_max:
            peeks += 1
            print 'Peek #', peeks
            print k, v
    print count_counter(cntr)
    
    
    print len(assocs)
    for k, v in sorted(cntr.items(), key=lambda x : x[0]):
        print k, v

def global_inspection(lang):
    builder = FactFinderBuilder(lang)
    (skill_implies_skill, skill_implies_occupation, occupation_implies_skill,
                          occupation_implies_occupation, occupation_is_more_junior,
                          occupation_is_more_senior, occupation_is_similar_to) =  builder.build_dics()
    ##########
    print 'occupation_implies_skill'
    inspect_assocs(occupation_implies_skill, 10)
    print 'skill_implies_skill'
    inspect_assocs(skill_implies_skill, 8)
    print 'occupation_implies_occupation'
    inspect_assocs(occupation_implies_occupation, 1)
    print 'occupation_is_more_junior'
    inspect_assocs(occupation_is_more_junior, 1)
    print 'occupation_is_more_senior'
    inspect_assocs(occupation_is_more_senior, 1)
    print 'occupation_is_similar_to'
    inspect_assocs(occupation_is_similar_to, 2)


if __name__ == '__main__':
    global_inspection('en')


