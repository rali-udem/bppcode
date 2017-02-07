import unittest
import json
from bppgen.letter.letter import build_data_insight, build_letter_generator
import os
from bppgen.data.data_access import Normalizer
from testutils import test_candidate, test_offer
from bppgen.letter.factfinder import load_dic

generator_fn = build_letter_generator

def make_dummy_profile(experience_functions, skills, pitch = ""):
    idx = 2016
    xp = []
    for experience_function in experience_functions :
        endDate = "{0}-05".format(idx)
        if idx == 2016:
            endDate = None
        xp.append({u"startDate":"{0}-05".format(idx -1),u"endDate":endDate,
                   u"function":experience_function,
                   u"place":"Toronto","missions":"",u"companyName":"cmp{0}".format(idx),
               u"company_id":"55df1c8d0b0451dc5c8bacc1"})
        idx -= 1
    skill_ls = []
    for skill in skills:
        skill_ls.append({u"name":skill})
    return {
        "countryCode":"CA",
          "city":"TORONTO","industry":"Accounting",
          "industryId":{"$numberLong":"48"},
          "industriesId":[{"$numberLong":"48"}],
          "relationsNumber":{"$numberLong":"500"},
          "personalBranding_pitch":pitch,
          u"experiences":xp,
            "educations":[{"startDate":"2011","endDate":"2013","name":""}],
            u"skills": skill_ls,
         "languages":[{"name":"English","level":"Full professional proficiency"},
                      {"name":"Urdu","level":"Native or bilingual proficiency"},
                      {"name":"Hindi","level":"Native or bilingual proficiency"},
                      {"name":"Arabic","level":"Limited working proficiency"}],
         "language":"en","langid":"en"}
    
def make_dummy_offer(offer_title, skills, noise_skills = [], company_name = "Some Company"):
    descr = u' '.join(skills) + u' '.join(noise_skills)
    return {"description":descr,
            "title":offer_title,
            "url":"http:/ee","ref_external":"74cdb930ee044d4c",
            "place":"Lower Mainland, BC",
            "company_name":company_name,
            "job_id":"INDEEDJOBSPIDER74cdb930ee044d4c","langid":"en"}

class TestLetter(unittest.TestCase):
    def inspect_simple(self):
        offer = test_offer()["java2"]
        candidate = test_candidate()["java2"]
        new_lexicon = {"what": {
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
    }
        data = {'offer' : offer, 'candidate' : candidate,
                'generation_data' : {
                                 "lang" :u"en",
                                 "formality" : 1,
                                 "psy" :u"I"
            }
            }
        gen = generator_fn("en")
        gen.generate(data)

class TestDataInsightSelector(unittest.TestCase):
    def test_simple(self):
        o = make_dummy_offer(u"solicitor", [u"C", u'privacy law', u'litigation'])
        p = make_dummy_profile([u"solicitor"],
                               [u'c', u'civil litigation', u'legal advice', u'corporate law',
                                u"privacy law"], u"wow privacy law!")
        di = build_data_insight("en")
        a = di.content_selection_data(
                        {'offer' : o, 'candidate' : p})
        (relevant_proficiency, relevant_expertise,
                    inferred_requirements_profile_skills,
                    explicit_offer_skill_covered_only_by_experience,
                    implicit_offer_skill_covered_only_by_experience,
                    target_occupation_implied_skills,
                    similar_current_occupation, similar_previous_occupations,
                    same_current_occupation, same_previous_occupations,
                    junior_current_occupation, junior_previous_occupations) = a
        

        self.assertTrue(u'privaci law' in relevant_expertise)
        self.assertTrue(u'c' in relevant_proficiency)
        
        self.assertTrue( (u'legal write', u'solicitor') in implicit_offer_skill_covered_only_by_experience)
        self.assertTrue( (u'litig', u'solicitor') in explicit_offer_skill_covered_only_by_experience)
        data = {'offer' : o, 'candidate' : p,
                'generation_data' : {
                                 "lang" :u"en",
                                 "formality" : 1,
                                 "psy" :u"I"
            }}
        f = di.content_selection({'offer' : o, 'candidate' : p})


class TestNormalizer(unittest.TestCase):
    def test_normalize_ngram(self):
        n = Normalizer(lang="en")
        n.normalize_ngram("laboratory technician")
        n = Normalizer(lang="fr")
        n.normalize_ngram("technicien de laboratoire")

if __name__ == '__main__':
    unittest.main()