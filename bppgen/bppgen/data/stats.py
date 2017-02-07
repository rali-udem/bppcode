#!/usr/bin/env python
# coding=utf-8
'''
Created on Jun 2, 2016

@author: bighouse
'''
from collections import Counter
from _collections import defaultdict
from itertools import combinations
import math

class Cooccurrence():
    def __init__(self, max_orders = 2, key=lambda x : x, base = 1):
        self.base = base
        self.key = key
        self.max_orders = max_orders
        self.cnts = []
        self.totals = Counter()
        self.records = 0
        self.record_idx = Counter()
        self.record_sizes = Counter()
        self.element_idx = defaultdict(lambda : {'keys':defaultdict(set), 'count' : 0})
        for _ in xrange(self.base, self.max_orders + 1):
            self.cnts.append(Counter())
    
    def __idx(self, i):
        return i - self.base
    
    def __key(self, items):
        return tuple(sorted(set(items)))
    
    def add_bipartite(self, ls1, ls2):
        self.record_sizes[len(ls1) * len(ls2)] += 1
        self.records += 1
        # A key may not be seen more than once. Imagine [1, 3, 4, 5] [1, 3, 4, 5]
        seen_keys = set()
        
        for item1 in ls1:
            for item2 in ls2:
                key = self.__key([item1, item2])
                if key in seen_keys :
                    raise Exception('Input iterables {0} and {1} are not disjoint or set like.'.format(ls1, ls2))
                self.cnts[1][key] += 1
                self.totals[1] += 1
                self.element_idx[item1]['keys'][1].add(key)
                self.element_idx[item2]['keys'][1].add(key)
            
            key1 = self.__key([item1])
            self.cnts[0][key1] += 1
            self.totals[0] += 1
            self.element_idx[item1]['keys'][0].add(key1)
            
        for item2 in ls2:
            key2 = self.__key([item2])
            self.cnts[0][key2] += 1
            self.totals[0] += 1
            self.element_idx[item2]['keys'][0].add(key2)
            
    
    def add(self, items):
        self.record_sizes[len(items)] += 1
        self.records += 1
        for order in xrange(self.base, self.max_orders + 1):
            for combo in combinations(items, order):
                key = self.__key(combo)
                self.cnts[self.__idx(order)][key] += 1
                self.totals[order] += 1
                for i in combo:
                    self.element_idx[i]['keys'][order - self.base].add(key)
                
    def __prob(self, key):
        order = len(key)
        cnt = self.cnts[self.__idx(order)]
        return float(cnt[key]) / self.records

    def prob(self, items):
        return self.__prob(self.__key(items))
    
    def count(self, *elems):
        return self.cnts[len(elems) - self.base][self.__key(elems)]
    
    def most_common(self, n, condition = lambda x : True):
        ls = self.cnts[0].most_common()
        ls = filter(lambda x : condition(x[0]), ls)
        return ls[:n]
    
    def add_record(self, collocs):
        '''
        Adds a record with only selected co-occurrences. Allows for much greater flexibility.
        Only supported for pairs.
        '''
        self.records += 1
        unique_items = set()
        
        # CHECK FOR DOUBLES
        keys = set()
        for colloc in collocs :
            key = self.__key(colloc)
            if key in keys:
                raise Exception('Key is double.')
            else:
                keys.add(key)
                
        # ADD THE KEY
        for key in keys:
            if len(key) != 2:
                raise Exception("Cannot handle adding a record this way.")
            order = len(key)
            self.cnts[1][key] += 1
            self.totals[1] += 1
            self.element_idx[key[0]]['keys'][1].add(key)
            self.element_idx[key[1]]['keys'][1].add(key)
            unique_items.add(key[0])
            unique_items.add(key[1])
        
        # ADD THE INDIVIDUALS
        for i in unique_items:
            key = self.__key([i])
            self.cnts[0][key] += 1
            self.totals[0] += 1
            self.element_idx[i]['keys'][0].add(key)
    
    '''
    Priors are a list of group of items
    '''
    def _joint_key(self, posteriors, priors):
        return self.__key(set(priors).union(set(posteriors)))
    
    def cond_prob(self, posteriors, priors):
        key_priors = self.__key(priors)
        order_priors = len(key_priors)
        key_total = self._joint_key(priors, posteriors)
        order_total = len(key_total)
        if key_priors not in self.cnts[self.__idx(order_priors)] :
            return 0.0
        elif key_total not in self.cnts[self.__idx(order_total)] :
            return 0.0
        return self.prob(key_total) / self.prob(key_priors)
    
    def pmi(self, posterior, priors):
        joint_key = self._joint_key(priors, posterior)
        return math.log(self.prob(joint_key)) - math.log(self.prob(posterior)) - math.log(self.prob(priors))
    
    def mi(self, v):
        res = 0.0
        for item in self.element_idx[v]['keys'][1]:
            res += self.prob([v, item[0]]) * self.pmi([v], [item[0]])
        return res
    
    def all_mis(self):
        ls = []
        for v in self.element_idx:
            ls.append((v, self.mi(v)))
        ls.sort(key=lambda x : x[1])
        return ls
    
def similarity(coocs, elem1, elem2):
    
    pass
    
    def __str__(self):
        return ' '.join(['Cooccurrences of max order', str(self.max_orders), 'and', str(len(self.element_idx)), 'distinct items'])
    

