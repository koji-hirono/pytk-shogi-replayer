# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogi import Coords, Move

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
    color = ['black', 'white']
    step = 0
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line[0] == '[':
            continue
        for token in line.split():
            if token.endswith('.'):
                #print('original step = {}'.format(token[:-1]))
                continue
            elif token[0].isdigit():
                #print('result = {}'.format(token))
                continue
            elif token[0] == '+':
                token = token[1:]
            #print('token = "{}"'.format(token))
            if token[1] == '*':
                dst = Coords(token[2], RANKNUM[token[3]])
                #print('dst file = {} rank = {}'.format(dst.file, dst.rank))
                #print('piece = {}'.format(token[0]))
                yield Move(color[step & 1], dst, None, token[0], None)
            else:
                src = Coords(token[1], RANKNUM[token[2]])
                dst = Coords(token[4], RANKNUM[token[5]])
                if token[-1] == '+':
                    promote = True
                else:
                    promote = False
                #print('src file = {} rank = {}'.format(src.file, src.rank))
                #print('dst file = {} rank = {}'.format(dst.file, dst.rank))
                yield Move(color[step & 1], dst, src, None, promote)
            step += 1

