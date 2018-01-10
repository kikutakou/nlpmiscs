#!/usr/bin/env python

import sys
import MeCab
from graphviz import Digraph


# launch mecab
format = r'%pi\t%ps\t%pe\t%m\t%H\t%s\t%pw\t%pC\t%pc\t%pb\n'
option = ["-F" + format, "-E" + format, "-a"]
option.extend(sys.argv[1:])
m = MeCab.Tagger(" ".join(option))

for line in sys.stdin:

    G = Digraph(engine='dot')
    G.attr('node', shape='box')

    s = Digraph('subgraph')
    s.graph_attr.update(rank='min')

    parsed = [line.split("\t", 9) for line in m.parse(line).split("\n")]
    list = sorted(parsed, key = lambda x:int(x[0]))

    # eos (bug?)
    eos = list[-1]
    eos[1] = str(int(eos[1]) - 1)
    eos[2] = str(int(eos[2]) - 1)
    eos[3] = "EOS"
    eos.extend(['']*6)
    eos[9] = "*"

    # root
    G.node('0', "BOS", color="red")

    # nodes
    for l in list:
        print(l)
        name = l[0]
        surface = l[3]
        isbest = l[9]
        isunk = (l[5] == '1')
        color = 'red' if isbest == "*" else 'black'
        style = 'dashed' if isunk else 'solid'

        pos = ",".join(filter(lambda x: x!="*", l[4].split(",")[:4]))
        text = "{}\n{}".format(surface + isbest, pos)
        G.node(name, text, color=color, style=style)

    # edges
    for v in list:
        if v[1] == '0':
            G.edge('0', v[0])
        else:
            cands = filter(lambda l: l[2] == v[1], list)
            s = min(cands, key=lambda l:int(l[8]))
            G.edge(s[0], v[0])

    # rank
    G.body.append("{rank=max; " + eos[0] + ";}")


    G.render('text', view=True)
