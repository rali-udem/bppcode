import re
from syntax import var, TransformationRule, CANNED_SYMBOL, Node
import logging


PATTERN_WHITESPACE = ur'\s'

def maybe(s):
    return ur'(?:{0})?'.format(s)

def maybe_repeat(s):
    return ur'(?:{0})*'.format(s)

def pattern_list(s, sepa=u','):
    return u'{1}({0}){1}({2}.+)?'.format(s, maybe_repeat(PATTERN_WHITESPACE), sepa)

def exact(s):
    return ur'^{0}$'.format(s)

def group(s, name=None):
    if not name:
        return ur'({0})'.format(s)
    else:
        return ur'(?P<{0}>{1})'.format(name, s)


## NOTES
NOTE_SEPARATOR = u';'
PATTERN_NOTE = ur'\w+{0}={0}(?:\w+|\'.+?\')'.format(maybe_repeat(PATTERN_WHITESPACE))
PATTERN_NOTES = pattern_list(PATTERN_NOTE, sepa=NOTE_SEPARATOR)
PATTERN_NOTE_LIST = ur'{0}\[{1}\]{0}'.format(maybe_repeat(PATTERN_WHITESPACE), PATTERN_NOTES)

## PATTERNS
PATTERN_INT = ur'[1-9][0-9]*'
PATTERN_VAR = ur'X{0}'.format(PATTERN_INT)
NOT_ESCAPED_QUOTE = ur"(?<!\\)'"
PATTERN_STRING = ur'{0}(.*){0}'.format(NOT_ESCAPED_QUOTE)
PATTERN_NODE = ur'([A-Za-z_]{1,30})\((.*)\)'
PATTERN_EXPRESSION = ur'({0}|{1}|{2}|{3})({4})?'.format(PATTERN_NODE, PATTERN_STRING, PATTERN_VAR, PATTERN_INT, PATTERN_NOTE_LIST)
PATTERN_ARGUMENT_LIST = pattern_list(PATTERN_EXPRESSION)

RULE_PATTERN = ur'{0}.+{0}=>{0}(.)+{0}'.format(maybe_repeat(PATTERN_WHITESPACE))


LEAF_NODES = ["P", "N", "V", "A", "Pro", "D", "Adv", "C", "L"]

def parse_quoted_text(s):
    m = re.match(PATTERN_STRING, s, re.UNICODE)
    groups = m.groups()
    if len(groups) == 1 :
        return Node({"value" : groups[0], "type" : CANNED_SYMBOL})
    else :
        raise Exception()


def arguments(s):
    quoted = False
    escaped = False
    paren_level = 0
    children = []
    flushed = False
    accu = u""
    for c in s:
        flushed = False
        if c == u"\\" and quoted:
            escaped = True
        elif c == u"'" and not escaped:
            quoted = not quoted
        elif not quoted:
            if c == u"(":
                paren_level += 1
            elif c == u")":
                paren_level -= 1
            elif c == u',' and paren_level == 0:
                children.append(accu)
                flushed = True
                accu = u''
        if not flushed:
            accu += c
    if accu :
        children.append(accu)
    return children

def parse_node(s):
    m = re.match(PATTERN_NODE, s, re.UNICODE)
    groups = m.groups()
    if len(groups) == 2 :
        children = []
        for argument in arguments(groups[1]):
            children.append(parse(argument))
            
        node_head = groups[0]
        content = {"type" : node_head}
        # IF THIS NODE IS A TERMINAL
        if groups[0] in LEAF_NODES and len(children) == 1:
            content["value"] = children[0].content['value']
            return Node(content)
        else :
            return Node(content, children)
    else :
        raise Exception()
    
def read_notes(s):
    d = {}
    s = s.strip()[1:-1]
    for pair in s.split(NOTE_SEPARATOR):
        splitz = pair.split(u'=')
        if len(splitz) == 2 :
            val = splitz[1].strip()
            if re.match(ur"'.+?'", val):
                val = val[1:-1]
            d[splitz[0].strip()] = val
        else :
            raise Exception('Could not parse note {0}'.format(s))
    return d

def parse(raw):
    try :
        s = raw.strip()
        m = re.match(PATTERN_EXPRESSION, s, re.UNICODE)
        groups = m.groups()
        if len(groups) == 7:
            node = None
            if re.findall(exact(PATTERN_STRING + maybe(PATTERN_NOTE_LIST)), s, re.UNICODE):
                node = parse_quoted_text(s)
            elif re.findall(exact(PATTERN_INT), s, re.UNICODE):
                node = int(s)
            elif re.findall(exact(PATTERN_NODE + maybe(PATTERN_NOTE_LIST)), s, re.UNICODE):
                node = parse_node(s)
            elif re.findall(exact(PATTERN_VAR + maybe(PATTERN_NOTE_LIST)), s, re.UNICODE):
                node = var(s)
                
            if node:
                if groups[5]:
                    modifiers = read_notes(groups[4])
                    node.content['modifiers'] = modifiers
                return node
            else :
                raise Exception('Could not parse "{0}"'.format(s))
    except Exception as e :
        logging.error("\"{0}\" could not be parsed.".format(raw))
        raise e
    raise Exception()

def parse_rule(raw):
    parts = [parse(x) for x in re.split(ur'=>', raw, 2)]
    return TransformationRule(parts[0], parts[1])

