# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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

class Pos(object):

    def __init__(self, file, rank):
        if not rank.isdigit():
            rank = RANKNUM[rank]
        self.file = int(file)
        self.rank = int(rank)

    @property
    def row(self):
        return self.rank - 1

    @property
    def col(self):
        return 9 - self.file

def decoder(f):
    color = ['black', 'white']
    step = 0
    for line in f:
        line = line.strip()
        if line[0] == '[':
            pass
        elif line[0].isdigit():
            src = Pos(line[0], line[1])
            dst = Pos(line[2], line[3])
            if line[-1] == '+':
                promote = True
            else:
                promote = False
            yield color[step & 1], dst, src, None, promote
            step += 1
        elif line[0].isupper():
            dst = Pos(line[2], line[3])
            yield color[step & 1], dst, None, line[0], None
            step += 1
