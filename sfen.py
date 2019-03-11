 # -*- coding: utf-8 -*2

from __future__ import unicode_literals
from shogi import Position, Coords, BLACK, WHITE
import re

STARTPOS='lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'

token_spec = [
    ('COUNT', r'\d+'),
    ('PIECE', r'\+?[a-zA-Z]'),
    ('UNDEF', r'.')
]
token_regexp = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)

def decoder_square(s):
    for rank, t in enumerate(s.split('/')):
        row = []
        for m in re.finditer(token_regexp, t):
            k = m.lastgroup
            v = m.group(k)
            if k == 'UNDEF':
                raise ValueError(v)
            elif k == 'PIECE':
                row.append(v)
            elif k == 'COUNT':
                for _ in range(int(v)):
                    row.append(None)
        for file, piece in enumerate(reversed(row)):
            yield Coords(file + 1, rank + 1), piece

def decoder_inhand(s):
    n = 1
    for m in re.finditer(token_regexp, s):
        k = m.lastgroup
        v = m.group(k)
        if k == 'UNDEF':
            raise ValueError(v)
        elif k == 'PIECE':
            color = BLACK if v.isupper() else WHITE
            yield color, v.upper(), n
            n = 1
        elif k == 'COUNT':
            n = int(v)

def decoder(s):
    p = Position()
    t = s.split()
    for coords, piece in decoder_square(t[0]):
        p.set_square(coords, piece)
        if coords.file > p.nfiles:
            p.nfiles = coords.file
        if coords.rank > p.nranks:
            p.nranks = coords.rank
    if len(t) < 2:
        return p
    p.turn = {'b':BLACK, 'w':WHITE}[t[1]]
    if len(t) < 3 or t[2] == '-':
        p.step = 0
        return p
    for color, piece, n in decoder_inhand(t[2]):
        p.set_inhand(color, piece, n)
    if len(t) < 4:
        p.step = 0
    else:
        p.step = int(t[3]) - 1
    return p
