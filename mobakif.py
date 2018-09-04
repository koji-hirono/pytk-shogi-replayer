# -*- coding: utf-8 -*-

from __future__ import unicode_literals
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
    '▲': 'black',
    '△': 'white'
}

class Pos(object):
    def __init__(self, file, rank):
        self.file = int(file)
        self.rank = int(rank)

    @property
    def row(self):
        return self.rank - 1

    @property
    def col(self):
        return 9 - self.file

def decoder(f):
    prevdst = None
    for line in f:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
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
            dst = Pos(line[1], RANKNUM[line[2]])
        # print('dst file = {} rank = {}'.format(dst.file, dst.rank))

        m = re.search(r'(成)?\((\d)(\d)\)$', line)
        if m:
            src = Pos(m.group(2), m.group(3))
            # print('src file = {} rank = {}'.format(src.file, src.rank))
            if m.group(1) == '成':
                promote = True
            else:
                promote = False
            piece = None
        else:
            src = None
            promote = None
            piece = PIECE[line[3]]
        # print('color = {}'.format(color))
        # print('piece = {}'.format(piece))
        yield color, dst, src, piece, promote
        prevdst = dst
