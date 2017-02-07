#!/usr/bin/env python
# coding=utf-8

# Syntax tree manipulation utilities. This section of the code is the most in need of being corrected.
## HERE BE DRAGONS

CANNED_SYMBOL = "CANNED"
import copy
import logging

COMPACT_PRINTS = True

def escape(s):
    return s.replace(u'"', ur'\"').replace(u"'", ur"\'")

def _print_jsrealb(tree):

    c = tree.content
    
    if "type" in c and c["type"] == "CANNED" :
        return u'"{0}"'.format(escape(unicode(c["value"])))
    if tree.children :
        b = unicode(c["type"]) + u"(" + u", ".join(map(print_jsrealb, tree.children)) + u")"
    elif tree.is_var() and not "type" in c:
        b = u"<{0}>".format(tree.var_name)
    else :
        try:
            b = u'{0}("{1}")'.format(unicode(c["type"]), unicode(c["value"]))
        except KeyError as e :
            logging.error('Problem printing ' + str(tree.content))
            raise e
    if tree.content.has_key("modifiers") :
        for k, v in tree.content["modifiers"].items() :
            true_v = unicode(v)
            try :
                b += u".{0}({1})".format(k, int(true_v))
            except :
                if true_v in [u'true', u'false']:
                    b += u".{0}({1})".format(k, true_v)
                else :
                    b += u".{0}(\"{1}\")".format(k, true_v)
    return b

def print_jsrealb(tree):
    '''
        Takes a Node produced by GenText and writes it to JSRealB syntax.
    '''
    try:
        try :
            return _print_jsrealb(tree)
        except UnicodeEncodeError :
            tree.content["value"] = unicode(tree.content["value"], 'utf-8')
            return _print_jsrealb(tree)
        except UnicodeDecodeError :
            tree.content["value"] = unicode(tree.content["value"], 'utf-8')
            return _print_jsrealb(tree)
        except AttributeError :
            return u'{0}'.format(tree)
    except Exception as e:
        logging.error(tree)
        raise Exception('Failed to print {0}'.format(tree),e)



def compact_print(n):
    if isinstance(n, basestring):
        return u'{0}'.format(n)
    elems = []
    if "type" in n.content:
        elems.append(n.content["type"])
    if "modifiers" in n.content:
        elems += n.content["modifiers"].iteritems()
    if "value" in n.content:
        elems.append(n.content["value"])
    
    if not elems :
        return n.simple_print()
    elif n.children :
        elems.append('[{0}]'.format(', '.join([compact_print(x) for x in n.children])))
    return u'(' + u', '.join([repr(x) for x in elems]) + u')'
     

IDS = 0
def gensym():
    global IDS
    IDS += 1
    return "@" + str(IDS)

class Node(object):
    '''
    This object is a special tree allowing variables. This should be rewritten.
    '''
    
    def __init__(self, content, children = list(), var_name = None):
        self.content = content
        self.children = children
        self.var_name = var_name
        
    def is_var(self):
        return self.var_name is not None
    
    def copy(self):
        return Node(copy.deepcopy(self.content), [child.copy() for child in self.children], self.var_name)
    
    def get_vars(self):
        if self.children :
            v = set()
            for child in self.children :
                v = v.union(child.get_vars())
            return v
        elif self.is_var() :
            return set([self.var_name])
        else :
            return set()
    
    def parents(self, var_name, this_parent = None):
        if self.is_var() and self.var_name == var_name and this_parent :
            return [this_parent]
        elif not self.children :
            return []
        else :
            parents = []
            for child in self.children :
                parents += child.parents(var_name, this_parent = self)
            return parents
    
    def propagate(self, fn, mode = "prefix"):
        if mode == "postfix" :
            fn(self)
        for child in self.children :
                child.propagate(fn, mode)
        if mode == "prefix" :
            fn(self)
            
    def __repr__(self):
        if COMPACT_PRINTS:
            return compact_print(self).replace(u'\\', u'')
        return self.simple_print()
    
    
    def simple_print(self):
        return 'Node:({0}, {1}, {2})'.format(str(self.content), str(self.var_name), [child for child in self.children])
    
    def __str__(self, *args, **kwargs):
        return self.__repr__().encode('utf-8')
    
    def replace(self, var_name, subtree):
        if self.is_var() and self.var_name == var_name:
            return subtree
        elif not self.children :
            return Node(self.content, [], var_name = self.var_name)
        else :
            ls = []
            for child in self.children :
                if isinstance(child, basestring):
                    continue
                ls.append(child.replace(var_name, subtree))
            return Node(self.content, ls)
        
    def is_leaf(self):
        return self.children == False or len(self.children) == 0
    
    def leaves(self):
        return self.find_all(lambda x : x.is_leaf(), silent = True)
    
    def find(self, predicate, silent=False):
        try:
            if predicate(self):
                return self
        except Exception as e:
            if not silent:
                raise e
        for child in self.children:
            if not isinstance(child, Node):
                continue
            
            res = child.find(predicate, silent = silent)
            if res:
                return res
        return None
        
    def find_all(self, predicate, silent=False):
        results = []
        try:
            if predicate(self):
                results.append(self)
        except Exception as e:
            if not silent:
                raise e
        
        for child in self.children:
            results += child.find_all(predicate, silent = silent)
        return results
    
    def __eq__(self, o):
        if type(o) != type(self):
            return False
        if o :
            return o.content == self.content and o.children == self.children and o.var_name == self.var_name
        else :
            return False
    
    def __ne__(self, o):
        return not self.__eq__(o)
    
    def replace_node(self, pattern, replacement):
        if self == pattern :
            return replacement.copy()
        elif not self.children:
            return self.copy()
        else :
            new_children = []
            for child in self.children:
                if isinstance(child, Node):
                    new_children.append(child.replace_node(pattern, replacement))
            
            return Node(self.content, new_children)
        
    def split_variable_occurrence(self, var_name):
        '''
        ASSIGNS A NEW NAME TO DIFFERENT OCCURRENCES OF A VARIABLE
        '''
        if self.is_var() and self.var_name == var_name:
            new_var_name = gensym()
            return [new_var_name], var(new_var_name)
        elif not self.children :
            return [], self
        else :
            new_children = []
            new_vars = []
            for child in self.children :
                child_new_variables, child_node = child.split_variable_occurrence(var_name)
                new_vars += child_new_variables
                new_children.append(child_node)
            return new_vars, Node(self.content, new_children)



        
def bind(pattern, against):
    return __bind(pattern, against, {})

def __bind(pattern, against, bindings):
    
    if "matching_predicate" in pattern.content :
        if not pattern.content["matching_predicate"](against) :
            return None
    
    # Look inside the content of the realizer
    for key, value in pattern.content.iteritems():
        if key == "matching_predicate":
            continue
        if key not in against.content or against.content[key] != value:
            return None
    # If it has a variable name, it can be bound to. It can be impure, ie will appear in the bindings but\
    # still not be a free variable
    if pattern.var_name:
        var_name = pattern.var_name
        if var_name in bindings and bindings[var_name] != against:
            conflict = bindings[var_name]
            logging.debug("Variable conflict on " + var_name + ":" + str(against) + " but was " + str(conflict))
            return None
        else :
            bindings[var_name] = against.copy()
    # If the pattern has children, follow-them
    for i in xrange(len(pattern.children)) :
        try :
            child_binding = __bind(pattern.children[i], against.children[i], bindings)
            if child_binding is not None:
                bindings.update(child_binding)
            else:
                logging.debug("Failed matching children {0} AGAINST {1} {2}".format(pattern.children[i], against.children[i], bindings))
                return None
        except KeyError as _:
            return None
    return bindings

def match(pattern, against):
    matched_descendant = against.find(lambda x : bind(pattern, x), silent = False)
    if matched_descendant :
        bindings = bind(pattern, matched_descendant)
        bindings['HEAD'] = matched_descendant
        return bindings
    else :
        return None

def __delete_transformation_fn(x):
    try:
        del x.content["transformation_fn"]
    except KeyError :
        pass

class TransformationRule():
    def __init__(self, binding_pattern, transformation_tree, post_condition = lambda x : True):
        self.binding_pattern = binding_pattern
        self.transformation_tree = transformation_tree
        self.post_condition = post_condition
    
    def __str__(self):
        return [self.binding_pattern, self.transformation_tree].__str__()
    
    def __repr__(self):
        return self.__str__()
    
    def apply(self, tree):
        bindings = bind(self.binding_pattern, tree)
        if not bindings :
            return None
        return self._apply(self.transformation_tree, bindings)
    
    def _apply(self, transformation_tree, bindings):
        var_name = transformation_tree.var_name
        if var_name :
            if var_name in bindings :
                if "transformation_fn" in transformation_tree.content :
                    result = transformation_tree.content["transformation_fn"](bindings[var_name])
                    return result
                else :
                    return bindings[var_name].copy()
                
        new_children = []
        for transformation_tree_child in transformation_tree.children:
            new_children.append(self._apply(transformation_tree_child, bindings))
        new_content = copy.deepcopy(transformation_tree.content)
        #del new_content["transformation_fn"]
        return Node(new_content, new_children, var_name = None)
    
    def replace_once(self, tree):
        bindings = match(self.binding_pattern, tree)
        if bindings :
            matched_descendant = bindings['HEAD']
            new_descendant = self.apply(matched_descendant)
            return tree.replace_node(matched_descendant, new_descendant)
        else:
            return tree
    
    def replace_all(self, tree):
        last = tree
        while True:
            current = self.replace_once(last)
            if current == last:
                return last
            else:
                last = current
        return tree
        
        
def var(var_name):
    return Node({}, var_name = var_name)

def canned(value, modifiers = {}, **kwargs):
    var_name = None
    if "var_name" in kwargs:
        var_name = kwargs["var_name"]
        del kwargs["var_name"]
    return Node({"modifiers" : modifiers, "type":CANNED_SYMBOL, "value" : value}, var_name = var_name)

def n(n_type, *args, **kwargs):
    '''
    Main entry point to creating JsRealB node objects.
    '''
    var_name = None
    if "var_name" in kwargs:
        var_name = kwargs["var_name"]
    
    if not isinstance(n_type, basestring) :
        raise Exception("First argument must be a string, but instead was {0}".format(n_type))
    if len(args) == 0:
        return canned(n_type, kwargs)
    # If it is a leaf element.
    if len(args) == 1 and isinstance(args[0], basestring):
        content = args[0]
        return Node({"modifiers" : kwargs, "type":n_type, "value" : content}, var_name = var_name)
    
    else :
        children = []
        for x in args :
            if isinstance(x, basestring) :
                children.append(canned(x))
            elif isinstance(x, Node) :
                children.append(x)
            else:
                raise Exception('Child {0} is neither text or a realizer'.format(x))
        return Node({"modifiers" : kwargs, "type":n_type}, children, var_name=var_name)

