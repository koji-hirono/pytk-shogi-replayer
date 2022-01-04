# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogitk.shogi import Coords, Move, BLACK, WHITE, DROP, PROMOTE

COLOR = {
    '+': BLACK,
    '-': WHITE
}

PIECE = {
    'FU': 'P',
    'KY': 'L',
    'KE': 'N',
    'GI': 'S',
    'KI': 'G',
    'KA': 'B',
    'HI': 'R',
    'OU': 'K',
    'TO': '+P',
    'NY': '+L',
    'NK': '+N',
    'NG': '+S',
    'UM': '+B',
    'RY': '+R'
}

def decoder(f):
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line[0] == "'":
            # comment
            continue
        if line[0] in ['+', '-']:
            color = COLOR[line[0]]
            line = line[1:]
            if not line:
                continue
            dst = Coords(int(line[2]), int(line[3]))
            file = int(line[0])
            rank = int(line[1])
            if file == 0 and rank == 0:
                # drop
                yield Move(color, dst, None, PIECE[line[4:6]], modifier=DROP)
            else:
                src = Coords(file, rank)
                yield Move(color, dst, src, PIECE[line[4:6]])
