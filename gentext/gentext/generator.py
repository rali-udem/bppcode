import aggregator, lexicalizer, loader, syntax, common, realizer

# The Microplanner plans how the section will look like, given what it will say.
# The SectionGenerator
class Microplanner():
    def plan(self, data):
        raise NotImplemented()
class TextGeneratorI():
    def generate(self, input_data):
        raise NotImplemented()
class DocumentPlanner():
    def plan_document(self, input_data):
        raise NotImplemented()
class ContentSelector():
    def get_name(self):
        raise NotImplemented()
    def content_selection(self, input_data):
        raise NotImplemented()
class TrivialContentSelector():
    def __init__(self, facts, name="no_name"):
        self.facts = facts
        self.name = name
    def content_selection(self, input_data):
        return self.facts
    def get_name(self):
        return self.name
    
class TrivialSentencePlanner():
    def plan(self, aggregates):
        return aggregates

class TrivialStylist():
    def flatten_SENT_nodes(self, node):
        if node.content["type"] == "SENT":
            subtrees = []
            for subtree in node.children:
                subtrees += self.flatten_SENT_nodes(subtree)
            return subtrees
        else:
            return [node]
            
    def transform(self, trees):
        new_trees = []
        for tree in trees:
            if isinstance(tree, syntax.Node):
                new_trees += self.flatten_SENT_nodes(tree)
            else:
                new_trees.append(tree)
        return new_trees

class AppendingWriter():
    def __init__(self, lexicalizer, transformer = TrivialStylist()):
        self.lexicalizer = lexicalizer
        self.transformer = transformer
    def __first_pass(self, aggregates):
        trees = []
        for aggregate in aggregates:
            if isinstance(aggregate, common.Nucleus):
                trees.append(self.lexicalizer.lexicalize(aggregate))
            elif isinstance(aggregate, common.Fact):
                trees.append(self.lexicalizer.lexicalize(aggregate))
            elif isinstance(aggregate, syntax.Node):
                trees.append(aggregate)
            elif aggregate in [common.NEWLINE_COMMAND]:
                trees.append(aggregate)
        return trees
    def __smoothing_pass(self, trees):
        return self.transformer.transform(trees)
    def write(self, aggregates):
        results = self.__smoothing_pass(self.__first_pass(aggregates))
        return [syntax.print_jsrealb(x) for x in results]
    
class TrivialMicroplanner(Microplanner):
    def __init__(self, content = None, fn = None):
        if (content is not None) == (fn is not None) :
            raise Exception('Either content or fn must have a value')
        self.fn = fn
        self.content = content
    def plan(self, data):
        if self.content:
            return self.content
        else :
            return self.fn(data)
        
class TrivialDocumentPlanner(DocumentPlanner):
    def __init__(self, sections):
        self.sections = sections
    def plan_document(self, input_data):
        return self.sections

class FullMicroplanner(Microplanner):
    def __init__(self, content_selector, aggregator, sentence_planner):
        self.content_selector = content_selector
        self.aggregator = aggregator
        self.sentence_planner = sentence_planner
    def plan(self, data):
        selected_content = self.content_selector.content_selection(data)
        aggregates = self.aggregator.aggregate(selected_content)
        plan = self.sentence_planner.plan(aggregates)
        return plan

def flatten(ls):
    flattened = []
    for section in ls :
        if type(section) == type([]) :
            flattened += section
        else :
            flattened.append(section)
    return flattened

class TextGenerator(TextGeneratorI):
    def __init__(self, document_planner, writer, lang="en"):
        self.document_planner = document_planner
        self.writer = writer
        self.realizer = realizer.JSRealBRealizer(lang)
    
    def generate(self, input_data):
        aggregates = []
        for microplanner in self.document_planner.plan_document(input_data):
            microplan = microplanner.plan(input_data)
            if isinstance(microplan, basestring):
                aggregates.append(syntax.canned(microplan))
            else :
                try:
                    aggregates += microplan
                except TypeError :
                    aggregates.append(microplan)
        final_trees = self.writer.write(aggregates)
        return final_trees

    def generate_and_realize(self, input_data):
        final_trees = self.generate(input_data)
        return self.realizer.realize(final_trees)

# Master construction class
# entity_lexicalizer, structural_lexicalizer, relation_lexicalizer
def build_generator(sections,
                    lang,
                    lexicalizer_file,
                    aggregator_factory = lambda : aggregator.ConfiguredAggregator(),
                    sentence_planner_factory = lambda : TrivialSentencePlanner(),
                    lexicalizer_factory = lambda e_l, s_l, r_l, lex : lexicalizer.simple_lexicalizer(e_l, s_l, r_l, lex),
                    entity_lexicalizer_factory = lambda x : lexicalizer.TrivialEntityLexicalizer(x),
                    structural_lexicalizer_factory = lambda x : lexicalizer.SimpleBilingualStructuralLexicalizer(x),
                    relation_lexicalizer_factory = lambda x : lexicalizer.TrivialRelationLexicalizer(x),
                    writer_factory = lambda x : AppendingWriter(x)):
    
    microplanners = []
    for section in sections:
        current = None
        # If you have a complex thing generating, you should consider using Microplanner interface for clarity.
        if isinstance(section, Microplanner):
            current = section
        # Provide a string to generate canned text
        elif isinstance(section, basestring):
            current = TrivialMicroplanner(content=section)
        # Provide any function that generates trees
        elif callable(section):
            current = TrivialMicroplanner(fn=section)
        # Provide a content selector specifically made for this purpose
        elif isinstance(section, ContentSelector):
            current = FullMicroplanner(section, aggregator_factory(), sentence_planner_factory())
        # Provide a list of facts
        elif hasattr(section, '__iter__'):
            facts = [i for i in section] # As a list.
            if facts and isinstance(facts[0], common.Fact):
                current = FullMicroplanner(TrivialContentSelector(facts), aggregator_factory(), sentence_planner_factory())
        
        if not current:
            raise Exception('Illegal section {0}'.format(section))
        else :
            microplanners.append(current)
    
    if not microplanners :
        raise Exception('This generator is empty!')
    
    relation_conf, entity_conf, structure_conf, _, lexicon, _, _ = loader.load_lexicalizer(lexicalizer_file)
    
    lexicalizer = lexicalizer_factory(
        relation_lexicalizer_factory(relation_conf),
        entity_lexicalizer_factory(entity_conf),
        structural_lexicalizer_factory(structure_conf),
        lexicon)
    return TextGenerator(TrivialDocumentPlanner(microplanners),
                         writer_factory(lexicalizer), lang)


def build_nuclei_generator(sections, lexicalizer_file, lang):
    '''
    Factory method for a text generator, based on the nuclei method described in the Masters' Thesis.
    The sections can be extremely varied:
        - a subclass of Microplanner for full customization;
        - a string (or unicode) for canned text;
        - a callable object, that takes the input and outputs some text.
        - a ContentSelector, the intended use of the program.
    '''
    relation_conf, entity_conf, structure_conf, _, lexicon, nuclei_conf, nuclei_frames = loader.load_lexicalizer(lexicalizer_file)
    
    lex = lexicalizer.nuclei_lexicalizer(
        lexicalizer.TrivialRelationLexicalizer(relation_conf),
        lexicalizer.TrivialEntityLexicalizer(entity_conf),
        lexicalizer.SimpleBilingualStructuralLexicalizer(structure_conf),
        lexicalizer.TrivialRelationLexicalizer(nuclei_frames),
        lexicon)
    microplanners = []
    for section in sections:
        current = None
        # If you have a complex thing generating, you should consider using Microplanner interface for clarity.
        if isinstance(section, Microplanner):
            current = section
        # Provide a string to generate canned text
        elif isinstance(section, basestring):
            current = TrivialMicroplanner(content=section)
        # Provide any function that generates trees
        elif callable(section):
            current = TrivialMicroplanner(fn=section)
        # Provide a content selector specifically made for this purpose
        elif isinstance(section, ContentSelector):
            aggreg = aggregator.NucleiAggregator(nuclei_conf["nuclei"], nuclei_conf["nuclei_order"][section.get_name()])
            current = FullMicroplanner(section, aggreg, TrivialSentencePlanner())
        # Provide a list of facts
        elif hasattr(section, '__iter__'):
            facts = [i for i in section] # As a list.
            if facts and isinstance(facts[0], common.Fact):
                current = FullMicroplanner(TrivialContentSelector(facts), aggreg,
                                           TrivialSentencePlanner())
        if not current:
            raise Exception('Illegal section {0}'.format(section))
        else :
            microplanners.append(current)
    if not microplanners :
        raise Exception('This generator is empty!')
    return TextGenerator(TrivialDocumentPlanner(microplanners), AppendingWriter(lex), lang)
    
    
    