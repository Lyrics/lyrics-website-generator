import re
from enum import Enum, auto

class NodeType(Enum):
    ORIG = auto()
    TRANS = auto()

p_inter_refs = re.compile('\s')
p_inter_ref = re.compile(',')
p_ref = re.compile('^(?P<sign>[-+]?)(?P<position>\d+)(?::(?P<weight>\d+))?$')

def parse_mapping(s):
    refs_num = 0
    ref_num = 0
    cur_pos = 0
    result = list()
    for refs in p_inter_refs.split(s):
        l = list()
        if refs:
            for ref in p_inter_ref.split(refs):
                m = p_ref.match(ref)
                if m:
                    (sign, pos, weight) = m.groups()
                    p = int(pos)
                    w = int(weight) if weight else 1
                    if sign == '+':
                        cur_pos += p
                    elif sign == '-':
                        cur_pos -= p
                    else:
                        cur_pos = p
                    l.append((cur_pos, w))
                else:
                    raise Exception('Failed to parse a reference at {}:{}'.
                                    format(refs_num, ref_num))
                ref_num += 1
        result.append(l)
        refs_num += 1
        ref_num = 0
    return result

def get_components(l, threshold):
    ## Build a graph
    g = dict()
    for i in range(len(l)):
        g[(NodeType.TRANS, i)] = list()
        for (to, w) in l[i]:
            if w >= threshold:
                g[(NodeType.TRANS, i)].append((NodeType.ORIG, to))
                if (NodeType.ORIG, to) in g:
                    g[(NodeType.ORIG, to)].append((NodeType.TRANS, i))
                else:
                    g[(NodeType.ORIG, to)] = list([(NodeType.TRANS, i)])
    ## Find connected components
    components = list()
    while g:
        (key, queue) = g.popitem()
        if queue:
            component = set([key])
            while queue:
                k = queue.pop()
                component.add(k)
                if k in g:
                    queue += g.pop(k)
            components.append(component)
    return components
