from gentext.generator import ContentSelector
from bppgen.data.data_access import NormalizingExtractor
from gentext.common import Fact
from _collections import defaultdict


BLACKLIST = [u"s_excel", u"s_microsoft offic", u"s_microsoft", u"s_continu improv", u"s_microsoft excel"]

def find_offer_function(offer_title, occupation_trie):
    if offer_title.split() not in occupation_trie:
        found = occupation_trie.search(offer_title.split())
        if found:
            titles = [x for x in sorted(found, key=lambda x : len(x), reverse = True) if len(x) < 4]
            return u" ".join(titles[0])
        else:
            return None
    else:
        return offer_title

class JobPresentationSelector(ContentSelector):
    
    def __init__(self, lang, data_extractor, occupation_reference):
        self.lang = lang
        self.data_extractor = data_extractor
        self.occupation_reference=occupation_reference
        
    def get_name(self):
        return "presentation"
    
    def content_selection(self, input):
        offer = input['offer']
        raw_offer_title = self.data_extractor.offer_function(offer)
        offer_title = find_offer_function(raw_offer_title, self.occupation_reference)
        facts = []
        lexical_adjective_psy = 'flattery_' + input["generation_data"]["psy"]
        profile_psych = Fact('profile_psychology', [{lexical_adjective_psy}])
        facts.append(profile_psych)
        
        if offer_title:
            company_name = 'our_client'
            if u'company_name' in offer :
                company_name = offer[u'company_name']
            offer_descr = Fact('job_descr_employer', [{'o_' + offer_title}, {company_name}])
            facts.append(offer_descr)
        return facts

def extract_from_text(text, trie):
    splitted = text.split()
    found = trie.search(splitted)
    if not found:
        return []
    return [u' '.join(x) for x in found]

class DataInsightSelector(ContentSelector):
    
    def __init__(self, data_extractor, fact_finder, skill_trie, occupation_trie):
            self.data_extractor = data_extractor
            self.fact_finder = fact_finder
            self.skill_trie = skill_trie
            self.occupation_trie = occupation_trie
            
    def __extract_skills(self, x, reference_ls):
            ls = []
            for skill in reference_ls:
                if (x + u' ').find(skill + u' ') >= 0:
                    ls.append(skill)
            return ls
        
    def get_name(self):
        return "insight"
        
    def had_same_experience(self, offer, profile):
        offer_title = self.data_extractor.offer_function(offer)
        same_job = False
        similar_experiences = set()
        experiences_with_similar_skills = set()
        experience_is_previous = set()
        
        for experience in self.data_extractor.profile_experiences(profile):
            if u"function" in experience:
                experience_title = experience[u"function"]
                if experience_title == offer_title :
                    same_job = True
                elif self.similar_occupation(offer_title, experience_title):
                    similar_experiences.add(experience_title)
                elif self.similar_skills(offer_title, experience_title):
                    experiences_with_similar_skills.add(experience_title)
                elif self.experience_is_often_previous(offer_title, experience_title):
                    experience_is_previous.add(experience_title)
                    
        return same_job, similar_experiences, experiences_with_similar_skills, experience_is_previous
    
    def relevant_experience(self, relevant_experiences, current_profile_experience, experiences):
        current_occupation_qualifies = None
        previous_occupations_qualify = set()
        
        if relevant_experiences:
            if current_profile_experience and current_profile_experience[u'function'] in relevant_experiences:
                current_occupation_qualifies = current_profile_experience[u'function']
            for experience in experiences :
                iter_occupation = experience[u'function']
                if iter_occupation in relevant_experiences and iter_occupation != current_occupation_qualifies:
                    previous_occupations_qualify.add(iter_occupation)
        
        return current_occupation_qualifies, previous_occupations_qualify
        
    def content_selection_data(self, input):
        profile = input["candidate"]
        offer = input["offer"]
        
        offer_title = self.data_extractor.offer_function(offer)
        offer_title = find_offer_function(offer_title, self.occupation_trie)
            
        experiences = self.data_extractor.profile_experiences(profile)
        current_profile_experience = self.data_extractor.current_profile_experience(profile)
        
        ### OFFER SKILLS ###
        normalized_offer_text = self.data_extractor.offer_description_text(offer)
        offer_skills = set(extract_from_text(normalized_offer_text, self.skill_trie))
        
        ### PROFILE SKILLS ###
        profile_skills = set([x for x in self.data_extractor.profile_skills(profile) if x.split() in self.skill_trie])
        expert_in = set(extract_from_text(self.data_extractor.profile_text(profile), self.skill_trie))
        
        ### FACTS EXTRACTED FROM THE DATABASE ###
        skills_implied_from_offer_title = set(self.fact_finder.occupation_implies_skill[offer_title])
        ### SIMILAR OCCUPATIONS ###
        more_junior_occupations = self.fact_finder.occupation_is_more_junior[offer_title]
        junior_current_occupation, junior_previous_occupations = self.relevant_experience(more_junior_occupations,
                                                                current_profile_experience, experiences)
        
        similar_occupations = self.fact_finder.occupation_is_similar_to[offer_title]
        similar_current_occupation, similar_previous_occupations = self.relevant_experience(similar_occupations,
                                                                current_profile_experience, experiences)
        
        same_current_occupation, same_previous_occupations = self.relevant_experience(set([offer_title]),
                                                                current_profile_experience, experiences)
        
        skills_implied_from_experience = {}
        for experience in experiences:
            title = experience[u'function']
            s = self.fact_finder.occupation_implies_skill[title]
            for skill in s:
                if skill not in skills_implied_from_experience:
                    skills_implied_from_experience[skill] = title
        
        relevant_profile_skills = profile_skills.intersection(offer_skills)
        relevant_expertise = expert_in.intersection(relevant_profile_skills)
        relevant_proficiency = relevant_profile_skills.difference(relevant_expertise)
        relevant_skills_from_experience = set(skills_implied_from_experience.keys())
        
        inferred_requirements_profile_skills = relevant_profile_skills.intersection(skills_implied_from_offer_title)
        
        explicit_offer_skill_covered_by_experience = relevant_skills_from_experience.intersection(offer_skills)
        explicit_offer_skill_covered_only_by_experience = explicit_offer_skill_covered_by_experience.difference(relevant_profile_skills)
        
        implicit_offer_skill_covered_only_by_experience = skills_implied_from_offer_title.intersection(relevant_skills_from_experience)
        
        implicit_offer_skill_covered_only_by_experience = set([(x, skills_implied_from_experience[x]) for x in implicit_offer_skill_covered_only_by_experience])
        explicit_offer_skill_covered_only_by_experience = set([(x, skills_implied_from_experience[x]) for x in explicit_offer_skill_covered_only_by_experience])
        implicit_offer_skill_covered_only_by_experience = implicit_offer_skill_covered_only_by_experience.difference(explicit_offer_skill_covered_only_by_experience)
        
        return (relevant_proficiency,
                relevant_expertise,
                inferred_requirements_profile_skills,
                explicit_offer_skill_covered_only_by_experience,
                implicit_offer_skill_covered_only_by_experience,
                set([similar_current_occupation]),
                similar_previous_occupations,
                set([same_current_occupation]),
                same_previous_occupations,
                set([junior_current_occupation]),
                junior_previous_occupations,
                skills_implied_from_experience)


    def content_selection(self, input):
        (relevant_proficiency,
         relevant_expertise,
                    inferred_requirements_profile_skills,
                    explicit_offer_skill_covered_only_by_experience,
                    implicit_offer_skill_covered_only_by_experience,
                    similar_current_occupation,
                    similar_previous_occupations,
                    same_current_occupation,
                    same_previous_occupations,
                    junior_current_occupation,
                    junior_previous_occupations,
                    skills_implied_from_experience) = self.content_selection_data(input)
                    
        facts = []
        seen_entities = set(BLACKLIST)
        unary_relation_names = [
            (relevant_proficiency, "profile_skill_proficiency", "s_"),
            (relevant_expertise, "profile_skill_expertise", "s_"),
            (inferred_requirements_profile_skills, "inferred_required_profile_skill", "s_"),
            (same_previous_occupations, "same_previous_occupation", "o_"),
            (junior_previous_occupations, "junior_previous_occupation", "o_"),
            (similar_previous_occupations, "similar_previous_occupation", "o_")
            ]
        n_ary_relation_names = [
            (explicit_offer_skill_covered_only_by_experience, "explicit_offer_skill_covered_only_by_experience", ['s_', 'o_']),
            (implicit_offer_skill_covered_only_by_experience, "implicit_offer_skill_covered_only_by_experience", ['s_', 'o_'])
            ]
    
        for relation_data, relation_name, prefix in unary_relation_names:
            if not relation_data:
                continue
            for elem in relation_data:
                if not elem :
                    break
                entity_id = prefix + elem
                if entity_id not in seen_entities:
                    seen_entities.add(entity_id)
                    facts.append(Fact(relation_name, [{u"you"}, {entity_id}]))
                
        for relation_data, relation_name, prefix in n_ary_relation_names:
            if not relation_data:
                continue
            for elem_tuple in relation_data:
                idx = 0
                arglist = []
                has_seen_entities = False
                for arg in elem_tuple:
                    entity_id = prefix[idx] + arg
                    if entity_id in seen_entities:
                        has_seen_entities = True
                        break
                    else:
                        seen_entities.add(entity_id)
                        arglist.append(entity_id)
                        idx += 1
                if not has_seen_entities:
                    facts.append(Fact(relation_name, [{u"you"}] + arglist))
        return facts
