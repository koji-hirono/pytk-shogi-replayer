# -*- coding: utf-8 -*-

from __future__ import unicode_literals

BLACK, WHITE = 'black', 'white'
UPWARD, DOWNWARD, HORIZONTAL = 'upward', 'downward', 'horizontal'
LEFT, RIGHT, VERTICAL = 'left', 'right', 'vertical'
DROP, PROMOTE, NOTPROMOTE = 'drop', 'promote', 'notpromote'

class Position(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.square = []
        self.inhand = {}
        for color in [BLACK, WHITE]:
            self.inhand[color] = {}
            for piece in 'PLNSGBRK':
                self.inhand[color][piece] = 0
        self.turn = None
        self.step = None

    def load(self, parser):
        self.clear()
        row = []
        for k, v in parser:
            if k == 'square':
                if v == '/':
                    self.square.append(row)
                    row = []
                else:
                    row.append(v)
            elif k == 'turn':
                self.turn = v
            elif k == 'inhand':
                v, n = v
                if v.isupper():
                    self.inhand[BLACK][v] = n
                else:
                    self.inhand[WHITE][v.upper()] = n
            elif k == 'step':
                self.step = v
        if self.step is None:
            self.step = 1

    def get_square(self, pos):
        return self.square[pos.row][pos.col]

    def put_square(self, pos, piece):
        p = self.square[pos.row][pos.col]
        self.square[pos.row][pos.col] = piece
        return p

    def take_inhand(self, color, piece):
        self.inhand[color][piece.lstrip('+').upper()] -= 1

    def put_inhand(self, color, piece):
        self.inhand[color][piece.lstrip('+').upper()] += 1

class Coords(object):

    def __init__(self, file, rank):
        self.file = int(file)
        self.rank = int(rank)

    @property
    def row(self):
        return self.rank - 1

    @property
    def col(self):
        return 9 - self.file

class Move(object):

    def __init__(self, color, dst, src=None, piece=None, **kwargs):
        self.color = color
        self.piece = piece
        self.dst = dst
        self.src = src
        self.movement = kwargs.pop('movement', None)
        self.relative = kwargs.pop('relative', None)
        self.modifier = kwargs.pop('modifier', None)
        self.capture = None

class Movelog(object):

    def __init__(self):
        self.data = []

    def load(self, parser):
        self.data = [None]
        for m in parser:
            self.data.append(m)

    def normalize(self, position):
        prev_dst = None
        for m in self.data:
            if not m:
                continue
            if m.dst == 'same':
                m.dst = prev_dst
            if m.piece is None:
                m.piece = position.put_square(m.src, '')
            elif m.src is None:
                position.take_inhand(position.turn, m.piece)
            else:
                # todo
                m.piece = position.put_square(m.src, '')
            if m.color == WHITE:
                piece = m.piece.lower()
            else:
                piece = m.piece.upper()
            if m.modifier == PROMOTE:
                piece = '+' + piece
            m.capture = position.put_square(m.dst, piece)
            if m.capture != '':
                position.put_inhand(position.turn, m.capture)
            position.turn = WHITE if position.turn == BLACK else BLACK
            position.step += 1
            prev_dst = m.dst

    def forward(self, position, d):
        start = position.step
        end = start + d
        if end > len(self.data):
            return
        for m in self.data[start:end]:
            if m.src:
                position.put_square(m.src, '')
            else:
                position.take_inhand(position.turn, m.piece)
            if m.color == WHITE:
                piece = m.piece.lower()
            else:
                piece = m.piece.upper()
            if m.modifier == PROMOTE:
                piece = '+' + piece
            position.put_square(m.dst, piece)
            if m.capture != '':
                position.put_inhand(position.turn, m.capture)
            position.turn = WHITE if position.turn == BLACK else BLACK
        position.step += d

    def back(self, position, d):
        start = position.step - 1
        end = start - d
        if end < 0:
            return
        for m in self.data[start:end:-1]:
            position.turn = WHITE if position.turn == BLACK else BLACK
            if m.src:
                position.put_square(m.src, m.piece)
            else:
                position.put_inhand(position.turn, m.piece)
            position.put_square(m.dst, m.capture)
            if m.capture != '':
                position.take_inhand(position.turn, m.capture)
        position.step -= d

    def goto(self, position, n):
        cur = position.step - 1
        if n > cur:
            self.forward(position, n - cur)
        elif n < cur:
            self.back(position, cur - n)
