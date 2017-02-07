from _abcoll import MutableSequence
import copy, inspect
import logging

NEWLINE_COMMAND = u"#NEWLINE"

def GET_LOGGER():
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    name = mod.__name__
    if name == '__main__':
        name = mod.__file__
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    LOGGER = logger
    return LOGGER

class ChainedException(Exception):
    def __init__(self, message, cause):
        super(ChainedException, self).__init__(message + u', caused by ' + repr(cause))
        self.cause = cause

class Relation():
    def __init__(self, name, arity, arg_constraints = None, relation_constraints = dict(), plan_notes = None):
        self.name = name
        self.arity = arity
        self.arg_contraints = arg_constraints
        self.relation_constraints = relation_constraints
        if not plan_notes :
            self.plan_notes = {}
        else :
            self.plan_notes = plan_notes
        
    def verify_constraints(self, relation):
        if len(relation.args) != self.arity :
            return False
        return True

class Fact():
    def __init__(self, name, args, relation_type = None, plan_notes = None):
        self.name = name
        self.args = []
        self.plan_notes = plan_notes
        for arg in args :
            if isinstance(arg, MutableSequence) or isinstance(arg, set) :
                self.args.append(set(arg))
            else :
                self.args.append(set([arg]))
        self.relation_type = relation_type
    
    def arg_included(self, other, i):
        return all([x in other.args[i] for x in self.args[i]]) 
    
    
    def merge(self, other):
        idx = 0
        new_args = []
        already_updated_one = False
        for arg in copy.deepcopy(self.args):
            other_arg = other.args[idx]
            new_set = arg.union(other_arg)
            if arg != new_set:
                if already_updated_one:
                    return None
                else :
                    already_updated_one = True
                    new_args.append(new_set)
            else:
                new_args.append(arg)
            idx += 1
        return Fact(self.name, new_args)
    
    def same_arg(self, other, i):
        return self.arg_included(other, i) and other.arg_included(self, i)
    
    def count_single_facts(self):
        t = 1
        for arg in self.args:
            if arg:
                t = t * len(arg)
        return t
    def same_args(self, other):
        return all([self.same_arg(other, i) for i in xrange(len(self.args))])
    
    def __repr__(self):
        return self.name + "(" + ", ".join(["{" + ", ".join(map(lambda x : '"' + x + '"' , parallel_args)) + "}" for parallel_args in self.args]) + ")"

class Nucleus():
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return 'Nucleus[name={0}, args={1}]'.format(self.name, self.args)

def default_relation_types():
    return []

class RelationFactory():
    def __init__(self, relation_types, strict_mode = False):
        self.relation_types = relation_types
        self.strict_mode = strict_mode
        
    def make(self, name, args):
        if name in self.relation_types :
            return Fact(name, args, self.relation_type[name])
        elif not self.strict_mode :
            return Fact(name, args)
    
    def _merge_args(self, args1, args2, arity):
        new_args = []
        for i in xrange(arity):
            new_args.append(args1[i].union(args2[i]))
        return new_args
    
    def conjunction_argument_combine(self, rel1, rel2):
        if rel1.name == rel2.name :
            new_args = self._merge_args(rel1.args, rel2.args, len(rel1.args))
            return self.make(rel1.name, new_args)
        return None