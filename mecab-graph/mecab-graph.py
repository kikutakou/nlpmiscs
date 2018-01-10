#!/usr/bin/env python

import sys
import MeCab
from graphviz import Digraph
import tempfile

# launch mecab
format = r'%pi\t%ps\t%pe\t%m\t%H\t%s\t%pw\t%pC\t%pc\t%pb\n'
option = ["-F" + format, "-E" + format, "-a"]
option.extend(sys.argv[1:])
m = MeCab.Tagger(" ".join(option))

for line in sys.stdin:

    # mecab parse
    parsed = [line.split("\t", 9) for line in m.parse(line).split("\n")]
    morph_list = sorted(parsed, key = lambda x:int(x[0]))

    # eos (bug?)
    eos = morph_list[-1]
    eos[1] = str(int(eos[1]) - 1)
    eos[2] = str(int(eos[2]) - 1)
    eos[3] = "EOS"
    eos.extend(['']*6)
    eos[9] = "*"

    # render
    G = Digraph(engine='dot')
    G.attr('node', shape='box')

    # root
    G.node('0', "BOS", color="red")

    # nodes
    for l in morph_list:
        print(l)
        name = l[0]
        surface = l[3]
        isbest = (l[9] == "*")
        isunk = (l[5] == '1')
        
        color = 'red' if isbest else 'black'
        style = 'dashed' if isunk else 'solid'

        pos = ",".join(filter(lambda x: x!="*", l[4].split(",")[:4]))
        text = "{}\n{}".format(surface, pos)
        G.node(name, text, color=color, style=style)

    # edges
    for v in morph_list:
        if v[1] == '0':
            G.edge('0', v[0])
        else:
            cands = list(filter(lambda l: l[2] == v[1], morph_list))
            s = min(cands, key=lambda l:int(l[8]))
            G.edge(s[0], v[0])

    # rank
    G.body.append("{rank=max; " + eos[0] + ";}")

    # print
    temp = tempfile.NamedTemporaryFile()
    G.render(temp.name, view=True)
