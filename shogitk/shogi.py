# -*- coding: utf-8 -*-

from __future__ import unicode_literals

BLACK, WHITE = 'black', 'white'
DROP, PROMOTE, NOTPROMOTE = 'drop', 'promote', 'notpromote'

def LEFT(srclist, color, piece, dst):
    file = None
    for src in srclist:
        if file is None:
            file = src.file
        elif color == BLACK and src.file > file:
            file = src.file
        elif color != BLACK and src.file < file:
            file = src.file
    for src in srclist:
        if src.file == file:
            yield src

def RIGHT(srclist, color, piece, dst):
    file = None
    for src in srclist:
        if file is None:
            file = src.file
        elif color == BLACK and src.file < file:
            file = src.file
        elif color != BLACK and src.file > file:
            file = src.file
    for src in srclist:
        if src.file == file:
            yield src

def VERTICAL(srclist, color, piece, dst):
    for src in srclist:
        if color == BLACK:
            dy = src.rank - dst.rank
            dx = src.file - dst.file
        else:
            dy = dst.rank - src.rank
            dx = dst.file - src.file
        if dy == 1 and dx == 0:
            yield src

def UPWARD(srclist, color, piece, dst):
    for src in srclist:
        if color == BLACK:
            dy = src.rank - dst.rank
        else:
            dy = dst.rank - src.rank
        if dy > 0:
            yield src

def DOWNWARD(srclist, color, piece, dst):
    for src in srclist:
        if color == BLACK:
            dy = src.rank - dst.rank
        else:
            dy = dst.rank - src.rank
        if dy < 0:
            yield src

def HORIZONTAL(srclist, color, piece, dst):
    for src in srclist:
        if color == BLACK:
            dy = src.rank - dst.rank
            dx = src.file - dst.file
        else:
            dy = dst.rank - src.rank
            dx = dst.file - src.file
        if dy == 0 and abs(dx) > 0:
            yield src

def pawn_isreachable(dx, dy):
    return dx == 0 and dy == 1

def lance_isreachable(dx, dy):
    return dx == 0 and dy > 0

def knight_isreachable(dx, dy):
    return abs(dx) == 1 and dy == 2

def silver_isreachable(dx, dy):
    return abs(dx) == abs(dy) == 1 or pawn_isreachable(dx, dy)

def gold_isreachable(dx, dy):
    return (dx == 0 and abs(dy) == 1) or (abs(dx) == 1 and dy in (0, 1))

def bishop_isreachable(dx, dy):
    return abs(dx) == abs(dy)

def rook_isreachable(dx, dy):
    return dx == 0 or dy == 0

def king_isreachable(dx, dy):
    return abs(dx) <= 1 and abs(dy) <= 1

def horse_isreachable(dx, dy):
    return bishop_isreachable(dx, dy) or king_isreachable(dx, dy)

def dragon_isreachable(dx, dy):
    return rook_isreachable(dx, dy) or king_isreachable(dx, dy)

def isreachable(color, piece, dst, src):
    f = {
        'P':pawn_isreachable,
        'L':lance_isreachable,
        'N':knight_isreachable,
        'S':silver_isreachable,
        'G':gold_isreachable,
        'B':bishop_isreachable,
        'R':rook_isreachable,
        'K':king_isreachable,
        '+P':gold_isreachable,
        '+L':gold_isreachable,
        '+N':gold_isreachable,
        '+S':gold_isreachable,
        '+B':horse_isreachable,
        '+R':dragon_isreachable
    }
    if color == BLACK:
        dx = src.file - dst.file
        dy = src.rank - dst.rank
    else:
        dx = dst.file - src.file
        dy = dst.rank - src.rank
    return f[piece](dx, dy)


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

    def find_src(self, color, piece, dst):
        for rank in range(1, self.nranks + 1):
            for file in range(1, self.nfiles + 1):
                src = Coords(file, rank)
                v = self.get_square(src)
                if v is None:
                    continue
                if v.isupper():
                    e_piece = v
                    e_color = BLACK
                else:
                    e_piece = v.upper()
                    e_color = WHITE
                if color != e_color:
                    continue
                if piece != e_piece:
                    continue
                if isreachable(color, piece, dst, src):
                    yield src


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

    def isdrop(self):
        return self.modifier == DROP

    def ispromote(self):
        return self.modifier == PROMOTE


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
            elif m.src:
                m.piece = position.take_square(m.src)
            else:
                srclist = list(position.find_src(m.color, m.piece, m.dst))
                if len(srclist) == 0:
                    m.modifier = DROP
                    position.take_inhand(position.turn, m.piece)
                elif len(srclist) == 1:
                    m.src = srclist[0]
                    m.piece = position.take_square(m.src)
                else:
                    if m.relative:
                        srclist = list(m.relative(srclist, m.color,
                            m.piece, m.dst))
                    if m.movement:
                        srclist = list(m.movement(srclist, m.color,
                            m.piece, m.dst))
                    if len(srclist) == 1:
                        m.src = srclist[0]
                    else:
                        raise ValueError(srclist)
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
