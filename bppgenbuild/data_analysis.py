#!/usr/bin/env python
# coding=utf-8
import numpy
from sklearn.feature_extraction import DictVectorizer

from bpp.data.mongoaccess import BppMongoDataSource, DataGenerator
from _collections import defaultdict

import logging

class BppAnalysis() :
    def __init__(self, lang):
        self.data_generator = DataGenerator(lang=lang)
        self._skill_coocs = None
        self._profile_occupation_skills = None
        #Occupation Relation
        self.occupation_past_coocs = None
        self.occupation_since_coocs = None
        
        
    def profile_skills(self):
        if self._skill_coocs :
            return self._skill_coocs
        else :
            logging.debug('Loading skills cooccurrences')
            self._skill_coocs = self.data_generator.skill_coocs()
            logging.debug('Done loading skills cooccurrences')
            return self._skill_coocs
        
    def profile_occupation_skills(self):
        if self._profile_occupation_skills :
            return self._profile_occupation_skills
        else :
            logging.debug('Loading occupations-skills cooccurrences')
            self._profile_occupation_skills = self.data_generator.profile_occupation_skills()
            logging.debug('Done loading occupations-skills cooccurrences')
            return self._profile_occupation_skills
        
    
    def most_frequent_skills_for_occupation(self, occupation, normalizing = True):
        if normalizing :
            occupation = u'o_' + self.data_generator.extractor.normalizer.normalize_title(occupation)
        ls = [(k[1], v) for k, v in self.profile_occupation_skills().cnts[1].iteritems() if k[0] == occupation]
        ls.sort(key=lambda x : -x[1])
        return ls
    
    def most_frequent_occupations_for_skill(self, skill, normalizing = True):
        if normalizing :
            skill = u's_' + self.data_generator.extractor.normalizer.normalize_ngram(skill)
        ls = [(k[0], v) for k, v in self.profile_occupation_skills().cnts[1].iteritems() if k[1] == skill]
        ls.sort(key=lambda x : -x[1])
        return ls
    
    def skill_likelihood(self, skill, occupation, normalizing = True):
        if normalizing :
            skill = self.data_generator.normalizer.normalize_ngram(skill)
            occupation = self.data_generator.extractor.normalizer.normalize_ngram(occupation)
        proba = self.profile_occupation_skills().cond_prob(["s_" + skill], ["o_" + occupation])
        print self.profile_occupation_skills().cond_prob(["o_" + occupation], ["s_" + skill])
        return proba
    
    def related_skills(self, occupation, threshold = 10, relatedness = lambda coocs, x, y: coocs.cond_prob([x], [y])):
        coocs = self.profile_occupation_skills()
        occupation = u"o_" + self.data_generator.extractor.normalizer.normalize_title(occupation)
        other_idx = [x for x in coocs.element_idx[occupation]['keys'][1] if len(x) == 2 and coocs.cnts[1] >= threshold]
        ls = []
        for idx in other_idx:
            y = idx[0]
            x = idx[1]
            if idx[0] == occupation :
                x = idx[0]
                y = idx[1]
            ls.append((x, y, (coocs.cond_prob([x], [y]))))
        ls.sort(key=lambda x: x[2], reverse=True)
        return ls
    
    def similar_occupations(self, occupation, skill_depth = 40, commonality = 0.5, normalizing = True):
        if normalizing :
            occupation = u'o_' + self.data_generator.extractor.normalizer.normalize_title(occupation)
        if commonality > skill_depth :
            raise Exception
        def other_occupation_skills(other_occupation) :
            return set(map(lambda x:x[0], self.most_frequent_skills_for_occupation(other_occupation, normalizing = False))[:skill_depth])
        skills = other_occupation_skills(occupation)
        related_occupations = defaultdict(lambda : set())
        
        def other_skill_occupations(other_skill):
            return set(map(lambda x:x[0], self.most_frequent_occupations_for_skill(other_skill, normalizing = False))[:skill_depth])
        
        for skill in skills :
            for other_occupation in other_skill_occupations(skill):
                other_skills = other_occupation_skills(other_occupation)
                if float(len(skills.intersection(other_skills))) / len(skills) >= commonality :
                    related_occupations[other_occupation] = other_skills
        return related_occupations
    
    def sorted_similar_occupations(self, similar_occupations):
        ls = [(k, v) for k, v in similar_occupations.iteritems()]
        ls.sort(key=lambda x: len(x[1]), reverse=True)
        return ls
    
    def embedding(self):
        pass
