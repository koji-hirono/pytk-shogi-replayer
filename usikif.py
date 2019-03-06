# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogi import Coords, Move, BLACK, WHITE, DROP, PROMOTE

RANKNUM = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
        'f': 6,
        'g': 7,
        'h': 8,
        'i': 9
}

def decoder(f):
    color = [BLACK, WHITE]
    step = 0
    for line in f:
        line = line.strip()
        if line[0] == '[':
            pass
        elif line[0].isdigit():
            src = Coords(int(line[0]), RANKNUM[line[1]])
            dst = Coords(int(line[2]), RANKNUM[line[3]])
            if line[-1] == '+':
                modifier = PROMOTE
            else:
                modifier = None
            yield Move(color[step & 1], dst, src, None, modifier=modifier)
            step += 1
        elif line[0].isupper():
            dst = Coords(int(line[2]), RANKNUM[line[3]])
            yield Move(color[step & 1], dst, None, line[0], modifier=DROP)
            step += 1
