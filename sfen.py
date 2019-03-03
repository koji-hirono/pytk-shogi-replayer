 # -*- coding: utf-8 -*2

from __future__ import unicode_literals
from shogi import BLACK, WHITE
import re

token_spec = [
    ('COUNT', r'\d+'),
    ('PIECE', r'\+?[a-zA-Z]'),
    ('UNDEF', r'.')
]
token_regexp = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)

def decoder_square(s):
    for t in s.split('/'):
        for m in re.finditer(token_regexp, t):
            k = m.lastgroup
            v = m.group(k)
            if k == 'UNDEF':
                raise ValueError(v)
            elif k == 'PIECE':
                yield v
            elif k == 'COUNT':
                for _ in range(int(v)):
                    yield ''
        yield '/'

def decoder_inhand(s):
    n = 1
    for m in re.finditer(token_regexp, s):
        k = m.lastgroup
        v = m.group(k)
        if k == 'UNDEF':
            raise ValueError(v)
        elif k == 'PIECE':
            yield v, n
            n = 1
        elif k == 'COUNT':
            n = int(v)

def decoder(s):
    t = s.split()
    for v in decoder_square(t[0]):
        yield 'square', v
    if len(t) < 2:
        return
    yield 'turn', {'b': BLACK, 'w': WHITE}[t[1]]
    if len(t) < 3 or t[2] == '-':
        return
    for v, n in decoder_inhand(t[2]):
        yield 'inhand', (v, n)
    if len(t) < 4:
        return
    yield 'step', int(t[3])
