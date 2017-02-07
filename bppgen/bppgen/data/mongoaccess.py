#!/usr/bin/env python
# coding=utf-8
'''
Created on Jul 20, 2016

@author: bighouse
'''
from json import dumps
import io
from pymongo import MongoClient
from bson import ObjectId
from collections import Counter
import random
from data_access import Normalizer, RawMongoDataExtractor, nice_number_string, NormalizingExtractor
from stats import Cooccurrence
from sklearn.feature_extraction.dict_vectorizer import DictVectorizer

TEST = True


TEST_DB = 'bpp_test'
COMPLETE_DB = 'bpp'

DB_NAME = TEST_DB
OFFERS = 'offers'

def dictionarize(ls):
    return {elem:1.0 for elem in ls}

class MongoAccess():
    
    def __init__(self, db):
        self.db = MongoClient()[db]
        self.colls = {}
    
    def get_coll(self, coll_id):
        if coll_id not in self.colls:
            coll = self.db[coll_id]
            self.colls[coll_id] = coll
            return coll
        return self.colls[coll_id]
    
    def get_one(self, coll_id, oid = None):
        if not oid :
            return self.get_coll(coll_id).find_one()
        return self.get_coll(coll_id).find_one({"_id" : ObjectId(oid)})
    
    def count(self, coll_id, query_dict = {}):
        return self.get_coll(coll_id).count(query_dict)
    
    def get(self, coll_id, query_dict):
        return self.get_coll(coll_id).find(query_dict, no_cursor_timeout=True)
    
    def insert(self, coll_id, record):
        self.get_coll(coll_id).insert_one(record)
        
    def update(self, coll_id, record):
        self.get_coll(coll_id).update_one(record)
    
    def get_by_id(self, coll_id, _id):
        object_id = ObjectId(_id)
        results = self.get_coll(coll_id).find({"_id" : object_id})
        for e in results :
            if e :
                return e
        return None

class BppMongoDataSource :
    '''
    This class is the last to know anything about mongodb.
    '''
    def __init__(self, mongo_access = None, db_name = DB_NAME, candidate_coll_id = 'profiles', offer_coll_id = 'offers'):
        if not mongo_access :
            self.mongo_access = MongoAccess(db_name)
        else :
            self.mongo_access = mongo_access
            
        self.offer_coll_id = offer_coll_id
        self.candidate_coll_id = candidate_coll_id
    
    def get_offer(self, offer_id):
        offer = self.mongo_access.get_by_id(self.offer_coll_id, offer_id)
        del offer['_id']
        return dumps(offer)
    
    def get_profile(self, profile_id):
        profile = self.mongo_access.get_by_id(self.candidate_coll_id, profile_id)
        del profile['_id']
        return dumps(profile)
    
    def get_profiles(self, query_dict = {}, lang = None):
        if lang:
            query_dict["langid"] = lang
        return self.mongo_access.get(self.candidate_coll_id, query_dict)
    
    def count_profiles(self, lang = None):
        if lang:
            query_dict["langid"] = lang
        return self.mongo_access.count(self.candidate_coll_id)
    
    def get_offers(self, query_dict = {}, lang = None):
        if lang:
            query_dict["langid"] = lang
        return self.mongo_access.get(self.offer_coll_id, query_dict)


class Vectorizer():
    def __init__(self):
        self.idx = {}
        self.ref= {}
        self.current = 0
    
    def add(self, thing):
        if thing in self.ref:
            return self.ref[thing]
        else:
            val = self.current
            self.ref[thing] = val
            self.idx[val] = thing
            self.current += 1
            return val
    def __getitem__(self, item):
        return self.add(thing)
    
    

def save_reference(path, vectorizer):
    with io.open(path, encoding='utf8') as f:
        for k, v in vectorizer.ref.iteritems():
            f.write(k + u',' + k)

def load_reference(path):
    vectorizer = Vectorizer()
    with io.open(path, encoding='utf8') as f:
        for line in f:
            splitted=line.split(u',')
            idx = int(splitted[1])
            ref = splitted[0]
            vectorizer.ref[ref] = idx
            vectorizer.idx[idx] = ref
    return vectorizer

class Vectorize():
    def __init__(self):
        self.skill_vectorizer = Vectorizer()
        self.occupation_vectorizer = Vectorizer()
    
    def skill_coocs(self):
        coocs = Cooccurrence()

    
    

class DataGenerator():
    '''
    This class returns the objects, properly normalized. It is designed to connect to any data_source.
    It also produces adequate representations of retrieved data, such as cooccurrence matrices or lists according
    to needs..
    '''
    def __init__(self, lang = None, data_source = None, extractor = None, denormalizing = False):
        self.lang = lang
        self.skill_vectorizer = Vectorizer()
        self.occupation_vectorizer = Vectorizer()
        if data_source is None:
            self.data_source = BppMongoDataSource()
        else:
            self.data_source = data_source
        if extractor is None:
            self.extractor = NormalizingExtractor(denormalizing=denormalizing, lang=lang)
        else :
            self.extractor = extractor

    def profile_skill_counts(self, cutoff=0):
        c = Counter()
        errors = 0
        keys = 0
        error_s = set()
        for profile in get_profiles(lang=self.lang):
            try :
                for skill in self.extractor.profile_skills(profile) :
                    c[skill] += 1
            except KeyError as e :
                keys += 1
            except Exception as e:
                error_s.add(str(e))
                raise e
                errors += 1
        return c
    
        def approximate_age(self):
            return
    
    def profile_skill_coocs(self, threshold = 100):
        coocs = Cooccurrence(2)
        keys = 0
        discard_rare = self.profile_skill_counts()
        for profile in get_profiles(lang=self.lang):
            try :
                skills = self.extractor.profile_skills(profile)
                coocs.add(filter(lambda x : discard_rare[x] > threshold,
                                 skills))
            except KeyError as e :
                keys += 1
        return coocs

    def profile_occupation_skills(self, threshold = 100, cooc_level = 2, with_xp = True):
        '''
        with_xp : decides wether past experiences should be added to the correlation
        '''
        coocs = Cooccurrence(cooc_level)
        errors = 0
        for profile in self.data_source.get_profiles(lang=self.lang):
            try :
                skills = self.extractor.profile_skills(profile)
                occupations = self.extractor.profile_function_labels(profile)
                if not with_xp :
                    occupations = [occupations[0]]
                for occupation in occupations :
                    for skill in skills :
                        coocs.add([u's_' + skill, u'o_' + occupation])
            except KeyError as e :
                errors += 1
        return coocs
    
    def count_skills(self):
        cntr = Counter()
        for profile in self.data_source.get_profiles(lang=self.lang):
            try :
                for skill in self.extractor.profile_skills(profile) :
                    cntr[skill] += 1
            except KeyError as e :
                keys += 1
        return cntr
    
    def count_occupations(self):
        cntr = Counter()
        for profile in self.data_source.get_profiles(lang=self.lang):
            try :
                for function_labels in self.extractor.profile_function_labels(profile) :
                    cntr[function_labels] += 1
            except KeyError as e :
                keys += 1
        return cntr
    
    def profile_occupations(self, threshold):
        coocs = Cooccurrence(2)
        keys = 0
        discard_rare = self.profile_skill_counts(lang=self.lang)
        for profile in self.data_source.get_profiles(lang=self.lang):
            try :
                coocs.add(filter(lambda x : discard_rare[x] > threshold, self.extractor.profile_skills(profile)))
            except KeyError as e :
                keys += 1
    
    def profile_skill_list(self, cutoff=0):
        ls = []
        for profile in self.data_source.get_profiles(lang=self.lang):
            ls.append(self.extractor.profile_skills(profile))
        if not ls:
            raise Exception('No profiles found.')
        return ls
    
    def profile_occupation_list(self):
        ls = []
        for profile in self.data_source.get_profiles(lang=self.lang):
            ls.append(self.extractor.profile_function_labels(profile))
        if not ls:
            raise Exception('No profiles found.')
        return ls

    def profile_skill_matrix(self):
        v = DictVectorizer(sparse=True)
        skill_list = self.profile_skill_list()
        if not skill_list :
            raise Exception('No skills found! Check your data access.')
        return v, v.fit_transform(map(dictionarize, self.profile_skill_list()))
    
    # _list(selector, get_profiles(), is_list = True TODO
    def _list(self, selector, cursor):
        c = Counter()
        errors = 0
        for profile in get_profiles():
            try :
                for skill in profile[u'skills'] :
                    c[self.normalizer.normalize_ngram(skill[u'name'])] += 1
            except :
                errors += 1
        return c

    
    def occupation_to_skills_coocs(self):
        c = Counter()
        errors = 0
        for profile in self.data_source.get_profiles():
            last_function = self.extractor.profile_function_labels(profile)
            if last_function :
                last_function = last_function[0]
            else :
                continue
            try :
                for skill in self.extractor.profile_skills(profile) :
                    key = (last_function, skill)
                    c[key] += 1
            except :
                errors += 1
        print errors
        return c
    
def sample(source_coll, dest_coll = None, ratio = None, sample_size = None, query_dict = {}):
    
    if not ratio and not sample_size :
        raise Exception('Sample of unspecified size.')
    
    total = count(source_coll, query_dict)
    if ratio :
        sample_size = total * ratio
    sample_nos = set(random.sample(xrange(total), sample_size))
    idx = 0
    if not dest_coll:
        dest_coll = source_coll + '_sample_' + nice_number_string(sample_size)
    for record in _get(DB_NAME, source_coll, query_dict):
        if idx in sample_nos :
            print record
            ls = []
            if u'industriesId' in record :
                for e in record[u'industriesId'] :
                    ls.append(e[u'$numberLong'])
                record[u'industriesId'] = ls
            insert(DB_NAME, dest_coll, record)
        idx += 1


def matrix_test():
    gen = DataGenerator()
    v, mat = gen.profile_skill_matrix()
    for i in range(0, 300) :
        print v.get_feature_names()[i]


def access_test():
    source = BppMongoDataSource()
    offers_ok = u'description' in source.mongo_access.get_one('offers')
    profiles_ok = u'collectData' in source.mongo_access.get_one('candidates')
    return offers_ok and profiles_ok
        
if __name__ == '__main__' :
    access_test()

    
