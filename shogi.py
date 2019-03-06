# -*- coding: utf-8 -*-

from __future__ import unicode_literals

BLACK, WHITE = 'black', 'white'
UPWARD, DOWNWARD, HORIZONTAL = 'upward', 'downward', 'horizontal'
LEFT, RIGHT, VERTICAL = 'left', 'right', 'vertical'
DROP, PROMOTE, NOTPROMOTE = 'drop', 'promote', 'notpromote'


class Position(object):

    def __init__(self):
        self.nfiles = 0
        self.nranks = 0
        self.square = {}
        self.inhand = {}
        self.turn = None
        self.step = None

    def set_square(self, coords, piece):
        self.square.setdefault(coords.file, {})
        self.square[coords.file][coords.rank] = piece

    def get_square(self, coords):
        return self.square[coords.file][coords.rank]

    def put_square(self, coords, piece):
        p = self.get_square(coords)
        self.square[coords.file][coords.rank] = piece
        return p

    def take_square(self, coords):
        return self.put_square(coords, None)

    def set_inhand(self, color, piece, n):
        self.inhand.setdefault(color, {})
        self.inhand[color][piece] = n

    def get_inhand(self, color, piece):
        self.inhand.setdefault(color, {})
        self.inhand[color].setdefault(piece, 0)
        return self.inhand[color][piece]

    def put_inhand(self, color, piece):
        piece = piece.lstrip('+').upper()
        self.inhand.setdefault(color, {})
        self.inhand[color].setdefault(piece, 0)
        self.inhand[color][piece] += 1

    def take_inhand(self, color, piece):
        self.inhand[color][piece.lstrip('+').upper()] -= 1


class Coords(object):

    def __init__(self, file, rank):
        self.file = file
        self.rank = rank


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
                position.step += 1
                continue
            if m.dst == 'same':
                m.dst = prev_dst
            if m.modifier is DROP:
                position.take_inhand(position.turn, m.piece)
            elif m.src is None:
                pass
            else:
                m.piece = position.take_square(m.src)

            if m.color == WHITE:
                piece = m.piece.lower()
            else:
                piece = m.piece.upper()
            if m.modifier == PROMOTE:
                piece = '+' + piece
            m.capture = position.put_square(m.dst, piece)
            if m.capture:
                position.put_inhand(position.turn, m.capture)
            position.turn = WHITE if position.turn == BLACK else BLACK
            position.step += 1
            prev_dst = m.dst

    def forward(self, position, d):
        start = position.step + 1
        end = start + d
        if end > len(self.data):
            return
        for m in self.data[start:end]:
            if not m:
                continue
            if m.src:
                position.take_square(m.src)
            else:
                position.take_inhand(position.turn, m.piece)
            if m.color == WHITE:
                piece = m.piece.lower()
            else:
                piece = m.piece.upper()
            if m.modifier == PROMOTE:
                piece = '+' + piece
            position.put_square(m.dst, piece)
            if m.capture:
                position.put_inhand(position.turn, m.capture)
            position.turn = WHITE if position.turn == BLACK else BLACK
        position.step += d

    def back(self, position, d):
        start = position.step
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
            if m.capture:
                position.take_inhand(position.turn, m.capture)
        position.step -= d

    def goto(self, position, n):
        cur = position.step
        if n > cur:
            self.forward(position, n - cur)
        elif n < cur:
            self.back(position, cur - n)
