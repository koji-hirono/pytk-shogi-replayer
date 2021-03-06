# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogitk.shogi import Coords, Move, BLACK, WHITE, DROP, PROMOTE
import copy
import re

RANKNUM = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9
}

PIECE = {
    '歩': 'P',
    '香': 'L',
    '桂': 'N',
    '銀': 'S',
    '金': 'G',
    '角': 'B',
    '飛': 'R',
    '王': 'K',
    '玉': 'K',
    'と': '+P',
    '成香': '+L',
    '成桂': '+N',
    '成銀': '+S',
    '馬': '+B',
    '竜': '+R',
    '龍': '+R'
}

COLOR = {
    '▲': BLACK,
    '△': WHITE
}

def decoder(f):
    prevdst = None
    for line in f:
        if isinstance(line, bytes):
            try:
                line = line.decode('utf-8')
            except:
                try:
                    line = line.decode('shift_jis')
                except:
                    raise
        line = line.strip()
        m = re.match(r'\d+\.\s+(.+)', line)
        if not m:
            # print('unmatch {}'.format(line))
            continue
        line = m.group(1)
        # print('line = {}'.format(line))
        color = COLOR[line[0]]
        if line[1] == '同':
            dst = copy.deepcopy(prevdst)
        else:
            dst = Coords(int(line[1]), RANKNUM[line[2]])
        # print('dst file = {} rank = {}'.format(dst.file, dst.rank))

        m = re.search(r'(成)?\((\d)(\d)\)$', line)
        if m:
            src = Coords(int(m.group(2)), int(m.group(3)))
            # print('src file = {} rank = {}'.format(src.file, src.rank))
            if m.group(1) == '成':
                modifier = PROMOTE
            else:
                modifier = None
            piece = None
        else:
            src = None
            modifier = DROP
            piece = PIECE[line[3]]
        # print('color = {}'.format(color))
        # print('piece = {}'.format(piece))
        yield Move(color, dst, src, piece, modifier=modifier)
        prevdst = dst
