#!/usr/bin/env python
# coding=utf-8

# This module allows to access normalized data in a consistent way.
# Any application using a so-called 'Extractor' as a dependency will transform the fields the same way.

import re
from collections import Counter
from bs4 import BeautifulSoup
from _collections import defaultdict
from nltk.stem.porter import PorterStemmer
import copy
import langid

WORD_PATTERN = ur'''(?x)          
      \w+(?:-\w+)* 
      | \$?\d+(?:\.\d+)?%?
      | \.\.\.  
      | [][.,;"'?():_`-]'''

STOPWORDS = {
        "en" :[u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours',
    u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers',
    u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves',
    u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are',
    u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does',
    u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until',
    u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into',
    u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down',
    u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here',
    u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more',
    u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so',
    u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now'],
    
        "fr" : [u'alors', u'au', u'aucuns', u'aussi', u'autre', u'avant', u'avec', u'avoir', u'bon', u'car', u'ce', u'cela', u'ces', u'ceux', u'chaque', u'ci',
    u'comme', u'comment', u'dans', u'des', u'du', u'dedans', u'dehors', u'depuis', u'devrait', u'doit', u'donc', u'dos', u'début', u'elle', u'elles', u'en',
    u'encore', u'est', u'et', u'eu', u'fait', u'faites', u'fois', u'font', u'hors', u'ici', u'il', u'ils', u'je     juste', u'la', u'le',
    u'les', u'leur', u'là', u'ma', u'maintenant', u'mais', u'mes', u'mine', u'moins', u'mon', u'mot', u'même', u'ni', u'notre', u'nous',
    u'ou', u'où', u'par', u'parce', u'pas', u'peut', u'peu', u'plupart', u'pour', u'pourquoi', u'quand', u'que', u'quel', u'quelle', u'quelles', u'quels',
    u'qui', u'sa', u'sans', u'ses', u'seulement', u'si', u'sien', u'son', u'sont', u'sous', u'soyez', u'sur', u'ta', u'tandis', u'tellement', u'tels',
    u'tes', u'ton', u'tous', u'tout', u'trop', u'très', u'tu', u'voient', u'vont', u'votre', u'vous', u'vu', u'ça', u'étaient', u'état', u'étions',
    u'été',
    u'être']}


def _nice_number_string(i, order, letter):
    if i < order :
        return None
    else :
        return str(i / order) + letter

def nice_number_string(i):
    ls = [(10 ** 3, 'K'), (10 ** 6, 'M'), (10 ** 9, 'G')] 
    ls.reverse()
    for order, letter in ls :
        s = _nice_number_string(i, order, letter)
        if s :
            return s
    return str(i)

class LemmatizingStemmer():
    def __init__(self, lemmatizer):
        self.lemmatizer = lemmatizer
        
    def stem(self, token):
        return self.lemmatizer.lemmatize(token)

def snowball_stemmer(lang):
    if lang == 'en' :
        from nltk.stem.snowball import EnglishStemmer
        return EnglishStemmer()
    if lang == 'fr' :
        from nltk.stem.snowball import FrenchStemmer
        return FrenchStemmer()

def porter_stemmer(lang):
    return PorterStemmer()

class Normalizer():
    def __init__(self, lang, denormalizing = False, stem = True):
        self.lang = lang
        if denormalizing :
            self.denormalizer = defaultdict(lambda : Counter())
            self.denormalizing = True
        else :
            self.denormalizing = False
        if stem :
            self.stemmer = snowball_stemmer(lang)
        else :
            self.stemmer = None
            
    def normalize_token(self, token, denormalize_aware=True):
        if self.stemmer :
            result = self.stemmer.stem(token)
        else :
            result = token
        if self.denormalizing and denormalize_aware:
            self.denormalizer[result][token] += 1 
        return result
    
    def normalize_title(self, title):
        return self.normalize_ngram(title)
    
    def tokenize(self, s):
        return re.findall(WORD_PATTERN, s, re.UNICODE)
    
    def normalize_ngram(self, ngram):
        tokens = self.tokenize(ngram)
        result = []
        for token in tokens:
            n_token = self.normalize_token(token, denormalize_aware=False)
            if n_token in STOPWORDS[self.lang]:
                continue
            result.append(n_token)
        
        value = u" ".join(result)
        if self.denormalizing :
            self.denormalizer[value][ngram] += 1 
        return value
    
    def denormalize_token(self, normalized):
        if self.denormalizing :
            return self.denormalizer[normalized].most_common()[0][0]
    
    def denormalize_ngram(self, normalized):
        if self.denormalizing :
            tokens = re.split('[\s\n]+', normalized)
            result = []
            for token in tokens :
                result.append(self.denormalize_token(token))
            return " ".join(result)
    
    def noHTML(self, msg):
        soup = BeautifulSoup(msg, "lxml")
        return soup.get_text()

class RawMongoDataExtractor():
    def profile_skills(self, profile):
        try :
            return map(lambda x : x[u'name'], profile[u'skills'])
        except :
            return []
        
    def raw_offer_description(self, offer):
        return offer[u'description']
    
    def offer_description_text(self, offer):
        soup = BeautifulSoup(self.raw_offer_description(offer), "lxml")
        return soup.get_text()
    
    def profile_function_labels(self, profile):
        try :
            return map(lambda x : x[u'function'], profile[u'experiences'])
        except :
            return []
    
    def profile_text(self, profile):
        s = u""
        ls = []
        for experience in self.profile_experiences(profile):
            if u"missions" in experience:
                s += experience[u"missions"] + u" "
        if u"personalBranding_claim" in profile :
            s += profile[u"personalBranding_claim"] + u" "
        if u"personalBranding_pitch" in profile :
            s += profile[u"personalBranding_pitch"] + u" "
        return s
    
    def profile_experiences(self, profile):
        try :
            experiences = profile[u'experiences']
            for experience in experiences:
                if u'startDate' not in experience:
                    experience[u'startDate'] = None
                if u'endDate' not in experience:
                    experience[u'endDate'] = None
            return experiences
        except :
            return []
    
    def offer_function(self, offer):
        return offer[u'title']
    
    def offer_organization(self, offer):
        try:
            return offer[u'company_name']
        except Exception as e :
            return None

class NormalizingExtractor():
    
    def __init__(self, raw_extractor = RawMongoDataExtractor(), lang = None, normalizer = None, denormalizing = False):
        if not normalizer and not lang:
            raise Exception('Normalizer improperly configured')
        
        if not normalizer :
            self.normalizer = Normalizer(lang=lang, denormalizing=denormalizing)
        else :
            self.normalizer = normalizer
        self.raw_extractor = raw_extractor
    
    def profile_skills(self, profile):
        return [self.normalizer.normalize_ngram(x) for x in self.raw_extractor.profile_skills(profile)]
    
    def profile_experiences(self, profile):
        experiences = self.raw_extractor.profile_experiences(profile)
        ls = []
        for experience in experiences :
            current = copy.deepcopy(experience)
            if u"function" in experience :
                current[u"function"] = self.normalizer.normalize_title(experience[u'function'])
                ls.append(current)
        return ls
    
    def profile_lang(self, profile):
        if u"langid" in profile:
            return profile[u"langid"]
        else:
            return langid.classify(self.profile_text(profile))[0]
    
    def offer_lang(self, offer):
        if u"langid" in offer:
            return offer[u"langid"]
        else:
            return langid.classify(self.raw_offer_description(offer))[0]
    
    def offer_description_text(self, offer):
        return self.normalizer.normalize_ngram(self.raw_extractor.offer_description_text(offer))
    
    def current_profile_experience(self, profile):
        for experience in self.profile_experiences(profile):
            if experience[u'endDate']:
                continue
            else:
                return experience
        return None
    
    def profile_function_labels(self, profile):
        return map(self.normalizer.normalize_title, self.raw_extractor.profile_function_labels(profile))
    
    def offer_description(self, offer):
        return self.normalizer.noHTML(self.raw_extractor.offer_description(offer))
    
    def offer_function(self, offer):
        return self.normalizer.normalize_title(self.raw_extractor.offer_function(offer))
    
    def offer_skills(self, offer, extract_skills):
        if u"description" in offer:
            return extract_skills(offer[u"description"])
        return []
    
    def profile_text(self, profile):
        return self.normalizer.normalize_ngram(self.raw_extractor.profile_text(profile))
    
    def profile_claims(self, profile, extract_skills):
        s = self.profile_text(profile)
        if s :
            return extract_skills(s)
        return []
        
    
    #TODO : la ressource de Fabrizio
    def offer_organization(self, offer):
        return self.raw_extractor.offer_organization(offer)