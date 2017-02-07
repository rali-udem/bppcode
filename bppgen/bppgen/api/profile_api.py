#!/usr/bin/env python
# coding=utf-8
import json
from bppgen.api.api_client import ApiClient
from bppgen.api.default_api import DefaultApi


class BPPAPI():
    
    def __init__(self, base_url = "http://rali.iro.umontreal.ca/lbj", country = 'ca', lang='en', profile_coll = 'latest', offer_coll = 'latest'):
        self.country = country
        self.lang = lang
        self.profile_coll = profile_coll
        self.offer_coll = offer_coll
        self.api = DefaultApi(ApiClient(base_url))
    
    
    def fetch(self, query):
        listeResultats = self.api.query_profiles(coll="latest", country="ca", language="fr", q=query, nbresults=3)

        if listeResultats:
            for resultat in listeResultats:
                print "Score: ", resultat.score
                print "Id du profil", resultat.id
                print "==========="
            objDuProfilEnString = api.get_profile(coll='latest', id=listeResultats[0].id)
            objDuProfil = eval(objDuProfilEnString)
            return json.dumps(objDuProfil, encoding="utf-8")
        return None
    
    def get_profile(self, profile_id):
        profile = {}
        try :
            profile = eval(self.api.get_profile(self.profile_coll, profile_id))
        except :
            profile =self.api.get_profile(self.profile_coll, profile_id)
        return profile
    
    def query_offers(self, q):
        return self.api.query_offers(self.offer_coll, self.lang, q, 25)
        
    def query_profiles(self, q):
        return self.api.query_profiles(self.profile_coll, self.country, self.lang, q, 25)
    
    def get_offer(self, offer_id):
        offer = {}
        try :
            offer = eval(self.api.get_offer(self.offer_coll, offer_id))
        except :
            offer = self.api.get_offer(self.offer_coll, offer_id)
        return offer
