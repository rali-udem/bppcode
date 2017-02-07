#!/usr/bin/env python
# coding=utf-8

from gentext.common import NEWLINE_COMMAND
from gentext.generator import build_generator, build_nuclei_generator, TextGenerator, FullMicroplanner, ContentSelector
from gentext.syntax import canned, n
from bppgen.data.data_access import NormalizingExtractor, Normalizer
from bppgen.letter.content_selection import DataInsightSelector, JobPresentationSelector

import os
import io
import csv
import json
from gentext.common import Fact
from bppgen.letter.factfinder import FactFinder, FactFinderBuilder
from bppgen.data.trie import Trie, CountingTrie

FORMALITY_INFORMAL = 0
FORMALITY_FORMAL = 1
FORMAL_VERY_FORMAL = 2

def is_formal(data):
    return data['generation_data']["formality"] > FORMALITY_INFORMAL

def is_very_formal(data):
    return data['generation_data']["formality"] > FORMALITY_FORMAL

def is_sympathetic(data):
    return data['generation_data']["formality"] == FORMALITY_INFORMAL

def is_female(data):
    try :
        return data['generation_data']["gender"] == "f"
    except :
        return None

def is_doctor(data):
    return None

def is_lawyer(data):
    return None


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# TEXT CONFIGURATIONS
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

GREETINGS_VOCAB_EN = {
                      "address" : {
                                   "doctor" :u"Dr. ",
                                   "generic_male" :u"Mr. ",
                                   "generic_female" :u"Ms. ",
                                   "lawyer" :u"Mr. "
                                   },
                      "greeting" : {
                                    "informal" :u"Good day to you ",
                                    "formal" :u"Dear "
                                    },
                      "anonymous" :u"John Doe"
                      }


PRESENTATION_VOCAB_EN = {
                         "hook" : {
                                   "D" :u"Your profile suggests that you are not one to say no to new challenges. I happen to have one that will interest you.",
                                   "I" :u"Your profile suggests that you are a true team player, and I have a great opportunity to share. You certainly look ready to go outside your comfort zone.",
                                   "S" :u"Your profile suggests that you are a true team player, and I have a great opportunity to share.",
                                   "C" :u"Your profile suggests that you are a self-driven worker, who doesn't need anyone looking over your shoulder."
                                   },
                         
                         "who_am_i" : {
                                    "D" :u"I am a recruiter for LittleBigJob and I am looking for bold candidates like yourself.",
                                    "I" :u"I am a recruiter for LittleBigJob and I am looking for inspirational candidates like yourself.",
                                    "S" :u"I am a recruiter for LittleBigJob and I am looking for dependable candidates like yourself.",
                                    "C" :u"I am a recruiter for LittleBigJob and I am looking for independent candidates like yourself."
                                        }
                         }


PRESENTATION_VOCAB_FR = {
                         "hook" : {
                                   "D" :u"Votre profil suggère que vous ne reculez pas devant les nouveaux défis. J'en aurais justement à vous proposer.",
                                   "I" :u"Votre profil suggère que vous seriez une belle addition à une équipe dynamique. J'ai d'ailleurs une belle opportunité à partager.",
                                   "S" :u"Votre profil suggère que vous seriez une belle addition à une équipe dynamique.",
                                   "C" :u"Votre profil suggère que vous êtes un travailleur autonome, qui se passe de supervision et imprime sa marque sur son travail. J'ai une opportunité qui pourrait vous intéresser."
                                   },
                         
                         "who_am_i" : {
                                    "D" :u"Je suis recruteur pour LittleBigJob et je suis à la recherche de candidats fonceurs comme vous.",
                                    "I" :u"Je suis recruteur pour LittleBigJob et je suis à la recherche de candidats inspirants comme vous.",
                                    "S" :u"Je suis recruteur pour LittleBigJob et je suis à la recherche de candidats fiables comme vous.",
                                    "C" :u"Je suis recruteur pour LittleBigJob et je suis à la recherche de candidats responsables comme vous."
                                        }
                         
                         }

FAREWELL_FR = (u"Découvrez sans attendre cette très belle opportunité en suivant le lien suivant: LIEN LIEN.\n" +
                    u"Sélectionnez « Je suis intéressé(e) » et complétez le formulaire en fournissant vos coordonnées " +
                    u"pour en savoir plus et être contacté par le recruteur. Vous pourrez lors de cet échange " +
                    u"envisager toutes les possibilités pour ce poste.\n" +
                    u"Au plaisir de vous lire,\n" +
                    u"LittleBIGJob")

FAREWELL_EN = (u'Please find the job description in the following link: LINK LINK\n' +
               u'In order to make it to make it to the first stages, and be contacted confidentially, please select "I ' +
               u'am interested" and complete the short form. ' +
               u"I am confident that this unique opportunity in a dynamic environment will interest you!\n" +
               u"All the best," +
               u"\nLittleBIGJob")

GREETINGS_VOCAB_FR = {
                      
                      "address" : {
                                   "doctor" :u"Dr ",
                                   "generic_male" :u"Monsieur ",
                                   "generic_female" :u"Madame ",
                                   "lawyer" :u"Me "
                                   },
                      "greeting" : {
                                    "informal" :u"Bonjour ",
                                    "formal" :u""
                                    },
                      "anonymous" :u"Jean Untel"

                      }

OFFER_DESCR_VOCAB_EN = {
                        'position' : u'The position you are being considered for is ',
                        'prep' :u'with ',
                        }

OFFER_DESCR_VOCAB_FR = {
                        'position' :u'Le poste pour lequel vous êtes approché est ',
                        'prep' :u'à ',
                        }

def example_generation_data_en():
    return {
            "lang" :u"en",
            "formality" : 1,
            "psy" :u"A"
            }
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# VOCAB : This part of the text configuration is manly canned text.
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
VOCAB = {"en" : {
            'greetings' : GREETINGS_VOCAB_EN,
            'presentation' : PRESENTATION_VOCAB_EN,
            'offer_descr' : OFFER_DESCR_VOCAB_EN,
            'farewell' : FAREWELL_EN
            },

            "fr" : {
            "greetings" : GREETINGS_VOCAB_FR,
            'presentation' : PRESENTATION_VOCAB_FR,
            'offer_descr' : OFFER_DESCR_VOCAB_FR,
            'farewell' : FAREWELL_FR
            }
}

def get_canned(data):
    return VOCAB[data['generation_data']['lang']]

def choose_greeting(data):
        if is_sympathetic(data) :
            return get_canned(data)["greetings"]["greeting"]["informal"]
        else :
            return get_canned(data)["greetings"]["greeting"]["formal"]

def address(data):
    vocab = get_canned(data)
    if is_formal(data) :
        if is_doctor(data) :
            return vocab["greetings"]["address"]["doctor"]
        elif is_lawyer(data) :
            return vocab["greetings"]["address"]["lawyer"]
        elif is_female(data) :
            return vocab["greetings"]["address"]["generic_female"]
        else :
            return vocab["greetings"]["address"]["generic_male"]
    else :
        return ''

def name(data):
    vocab = get_canned(data)
    try :
        return profile['name']
    except :
        return vocab['greetings']["anonymous"]
    
def salutation(data):
    generation_data = data["generation_data"]
    return [canned(choose_greeting(data) +
                  address(data) +
                  name(data) +',')]

def bilingual_canned(lang, en_msg, fr_msg):
        if lang == u"fr":
            return fr_msg
        else:
            return en_msg

def presentation(lang):
        return bilingual_canned(lang,
        u"I write this email after having read your LinkedIn profile. My name is Joan, I am a recruiter with LittleBIGJob. Our company uses an artificial intelligence to make data-driven decisions in human resources. I only contact the best candidates based on statistical models, and you've made the short list.",
        u"J'écris ce courriel après avoir lu votre profil LinkedIn. Mon nom est Susanne, je suis recruteur chez LittleBIGJob. Notre compagnie utilise une intelligence articielle pour prendre des décisions dans le domaine des ressources humaines. Je ne contacte que les meilleurs candidats selon un modèle statistique, et vous êtes l'un d'eux.")

def contact(lang):
    return bilingual_canned(lang,
                    u"Would you be open to discuss this over the phone? When would you be available?",
                    u"Seriez-vous prêts à discuter de cette offre de vive voix? Quand seriez-vous disponible?")
    
def thank_you(lang):
    return bilingual_canned(lang,
                            u"Thank you for your time and your reply,",
                            u"Merci de votre temps et de votre réponse.")
def init_references(lang):
    skill_reference = read_denormalized('letter_data/{0}/lexicon_skill'.format(lang))
    occupation_reference = read_denormalized('letter_data/{0}/lexicon_job'.format(lang))
    skill_trie = CountingTrie()
    occupation_trie = CountingTrie()
    
    for k in skill_reference:
        skill_trie.add(k.split())
    for k in occupation_reference:
        occupation_trie.add(k.split())
    return skill_trie, occupation_trie

def build_data_insight(lang, data_extractor=None, skill_reference = None, occupation_reference = None):
    if data_extractor is None:
        data_extractor = NormalizingExtractor(normalizer=Normalizer(lang=lang, stem = True))
    if skill_reference is None:
        skill_reference, occupation_reference = init_references(lang)
    factfinder = FactFinderBuilder(lang).build()
    
    return DataInsightSelector(data_extractor, factfinder, skill_reference, occupation_reference)

def read_denormalized(filename):
    dico = {}
    with io.open(os.path.dirname(__file__) + '/' + filename, encoding = 'utf-8') as f:
        for line in f:
            splitted = line.split(u',')
            dico[unicode(splitted[0].strip())] = unicode(splitted[1].strip())
    return dico

def build_letter_generator(lang):
    dir = os.path.dirname(__file__)
    data_extractor = NormalizingExtractor(normalizer=Normalizer(lang=lang, stem = True))
    factfinder = FactFinderBuilder(lang).build()
    conf_file = 'letter_data/{0}/letter_conf.json'.format(lang)
    skill_trie, occupation_trie = init_references(lang)
        
    job_presentation_section = JobPresentationSelector(lang, data_extractor, occupation_reference=occupation_trie)
    insight_section = build_data_insight(lang, data_extractor=data_extractor,
                           skill_reference=skill_trie, occupation_reference=occupation_trie)
    sections = [
        salutation, NEWLINE_COMMAND,
        presentation(lang), NEWLINE_COMMAND,
        job_presentation_section, NEWLINE_COMMAND,
        insight_section, NEWLINE_COMMAND,
        contact(lang), NEWLINE_COMMAND,
        thank_you(lang)
        ]
    return build_nuclei_generator(sections, dir + '/' + conf_file, lang)

def generate_letter(offer, profile, generation_data):
    generator = build_letter_generator(generation_data['lang'])
    return generator.generate({"candidate" : profile, "offer" : offer, "generation_data" : generation_data})

def generate_and_realize_letter(offer, profile, generation_data):
    generator = build_letter_generator(generation_data['lang'])
    return generator.generate_and_realize({"candidate" : profile, "offer" : offer, "generation_data" : generation_data})

