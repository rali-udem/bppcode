#!/usr/bin/env python
# coding=utf-8
import subprocess, common, parse_syntax, re
from collections import defaultdict
import json, os

NEW_LEXICON_EN = {"what": {
        "Pro": {
            "tab": ["pn7","pn6"]
        }
    },
               "which": {
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
    },
               "infer" : {
    "V": {
     "tab": ["v13"]}
    }
}

NEW_LEXICON_FR = {
    u"déduire" : {"V": {
            "tab": "v113",
            "aux": ["av"]
        }},
    u"inférer" : {
        "V": {
            "tab": "v28",
            "aux": ["av"]
        }},
        u"suggérer" : {
        "V": {
            "tab": "v28",
            "aux": ["av"]
        }}
    
    }

NEW_LEXICON = {
    "fr" : NEW_LEXICON_FR,
    "en" : NEW_LEXICON_EN
    }

def as_paragraphs(ls):
    paras = []
    tmp = []
    for item in ls:
        if item == u'"{0}"'.format(common.NEWLINE_COMMAND):
            paras.append(tmp)
            tmp = []
        else :
            tmp.append(item)
    if tmp:
        paras.append(tmp)
    return paras

def extract_vocab(jsrealcode, d, lang):
    if lang == u'fr' :
        return extract_vocab_fr(jsrealcode, d)
    else :
        return extract_vocab_en(jsrealcode, d)

def extract_vocab_fr(jsrealcode, d):
    for l in parse_syntax.LEAF_NODES:
        for m in re.finditer(l + '\("(.*?)"\)', jsrealcode):
            word = m.groups(1)[0]
            if l == u'N' :
                if word[0].isalpha():
                    d[word][u'N'] = {"g": "m", "tab": ["n3"]}
                else:
                    d[word][u'N'] = {"g": "m", "tab": ["n3"]}
            elif l == u'P' :
                d[word][u'P'] = {"tab" : ["pp"]}
            elif l == u'A' :
                d[word][u'A'] = {"tab" : ["n28"]}
            elif l == u'Adv' :
                d[word][u'Adv'] = {"tab" : ["av"]}
            elif l == u'V' :
                d[word][u'V'] = {"tab": "v36", "aux": ["av"]}
            elif l == u'Pro' :
                d[word][u'Pro'] = {"tab" : ["pn5"]}
            elif l == u'D' :
                d[word][u'D'] = {"tab" : ["d3"]}

def extract_vocab_en(jsrealcode, d):
    for l in parse_syntax.LEAF_NODES:
        for m in re.finditer(l + '\("(.*?)"\)', jsrealcode):
            word = m.groups(1)[0]
            if l == u'N' :
                d[word][u'N'] = {"tab" : ["n1"]}
            elif l == u'P' :
                d[word][u'P'] = {"tab" : ["pp"]}
            elif l == u'A' :
                d[word][u'A'] = {"tab" : ["a1"]}
            elif l == u'Adv' :
                d[word][u'Adv'] = {"tab" : ["b1"]}
            elif l == u'V' :
                d[word][u'V'] = {"tab" : ["v1"]}
            elif l == u'Pro' :
                d[word][u'Pro'] = {"tab" : ["pn5"]}
            elif l == u'D' :
                d[word][u'D'] = {"tab" : ["d3"]}
    
def _extract_all_vocab(jsrealcodes, lang):
    d = defaultdict(dict)
    for jsrealcode in jsrealcodes:
        extract_vocab(jsrealcode, d, lang)
    return {k:v for k, v in d.items()}

    # The second vocabulary will override the first, in place.
def update_vocabs(v1, v2):
        for word, entry in v2.items():
            if word in v1:
                for syntagm_type, spec in entry.items():
                    v1[word][syntagm_type] = spec
            else:
                v1[word] = entry

def new_vocab(jsrealcodes, lang):
    extracted = _extract_all_vocab(jsrealcodes, lang)
    update_vocabs(extracted, NEW_LEXICON[lang])
    return extracted

class Realizer():
    def realize(self, code):
        raise NotImplementedError()

class JSRealBRealizer(Realizer):
    
    def __init__(self, lang):
        self.lang = lang
    
    def realize(self, codes):
        basedir = os.path.dirname(__file__)
        jsrealcmd = os.path.join(basedir, "jsrealcmd.js")
        jslib = os.path.join(basedir, 'jsreal', 'JSrealB-EnFr.js')
        extracted_vocab = new_vocab(codes, self.lang)
        return subprocess.check_output(["nodejs",
                                jsrealcmd,
                                jslib,
                                json.dumps(extracted_vocab),
                                json.dumps(codes),
                                self.lang])

