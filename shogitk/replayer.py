# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogitk.shogi import Coords, BLACK, WHITE
import shogitk.shogi as shogi
import shogitk.sfen as sfen
import shogitk.usikif as usikif
import shogitk.mobakif as mobakif
import shogitk.kif as kif
import shogitk.ki2 as ki2
import shogitk.psn as psn
import shogitk.csa as csa


def load_file(s, logfile):
    position = sfen.decoder(s)
    movelog = shogi.Movelog()
    if logfile.lower().endswith('.psn'):
        with open(logfile, 'r') as f:
            movelog.load(psn.decoder(f))
            movelog.normalize(position)
    elif logfile.lower().endswith('.usi'):
        with open(logfile, 'r') as f:
            movelog.load(usikif.decoder(f))
            movelog.normalize(position)
    elif logfile.lower().endswith('.csa'):
        with open(logfile, 'r') as f:
            movelog.load(csa.decoder(f))
            movelog.normalize(position)
    elif logfile.lower().endswith('.ki2'):
        with open(logfile, 'r') as f:
            movelog.load(ki2.decoder(f))
            movelog.normalize(position)
    elif logfile.lower().endswith('.kif'):
        fail = False
        with open(logfile, 'r') as f:
            movelog.load(mobakif.decoder(f))
            if len(movelog.data) < 2:
                fail = True
        if fail:
            with open(logfile, 'r') as f:
                movelog.load(kif.decoder(f))
        movelog.normalize(position)
    return position, movelog


class Replayer(object):

    def __init__(self, ui, movelog, position):
        self.ui = ui
        self.movelog = movelog
        self.position = position
        self.ui.control.first.configure(command=self.move_first)
        self.ui.control.last.configure(command=self.move_last)
        self.ui.control.prev1.configure(command=self.move_back)
        self.ui.control.next1.configure(command=self.move_forward)
        self.ui.movelog.tree.bind('<ButtonRelease-1>', self.move_goto)
        self.ui.menu.command['open_file'] = self.open_file

    def open_file(self, filename):
        s = sfen.STARTPOS
        self.position, self.movelog = load_file(s, filename)
        self.init()

    def init(self):
        self.movelog.goto(self.position, 0)
        step = self.position.step
        self.ui.control.curr_v.set(step)
        self.ui.movelog.clear()
        self.ui.movelog.load(self.movelog.data)
        self.update()

    def move_first(self):
        self.movelog.goto(self.position, 0)
        step = self.position.step
        self.ui.control.curr_v.set(step)
        self.ui.movelog.set_step(step)
        self.update()

    def move_last(self):
        self.movelog.goto(self.position, len(self.movelog.data) - 1)
        step = self.position.step
        self.ui.control.curr_v.set(step)
        self.ui.movelog.set_step(step)
        self.update()

    def move_back(self):
        self.movelog.back(self.position, 1)
        step = self.position.step
        self.ui.control.curr_v.set(step)
        self.ui.movelog.set_step(step)
        self.update()

    def move_forward(self):
        self.movelog.forward(self.position, 1)
        step = self.position.step
        self.ui.control.curr_v.set(step)
        self.ui.movelog.set_step(step)
        self.update()

    def move_goto(self, event):
        step = self.ui.movelog.get_step()
        self.movelog.goto(self.position, step)
        self.ui.control.curr_v.set(step)
        self.update()

    def update(self):
        step = self.position.step
        lastmove = None
        if step > 0 and step < len(self.movelog.data):
            lastmove = self.movelog.data[step]
        for rank in range(1, self.position.nranks + 1):
            for file in range(1, self.position.nfiles + 1):
                piece = self.position.get_square(Coords(file, rank))
                row = rank - 1
                col = self.position.nfiles - file
                self.ui.position.square.take(row, col)
                self.ui.position.square.clear_style(row, col)
                if lastmove:
                    if lastmove.src:
                        if lastmove.src.file == file and lastmove.src.rank == rank:
                            self.ui.position.square.set_style(
                                    lastmove.src.rank - 1,
                                    self.position.nfiles - lastmove.src.file)
                    if lastmove.dst:
                        if lastmove.dst.file == file and lastmove.dst.rank == rank:
                            self.ui.position.square.set_style(
                                    lastmove.dst.rank - 1,
                                    self.position.nfiles - lastmove.dst.file,
                                    stipple='gray75')
                if piece:
                    if piece.isupper():
                        p = piece
                        side = 'downside'
                    else:
                        p = piece.upper()
                        side = 'upside'
                    self.ui.position.square.put(side, p, row, col)
        for color, data in self.position.inhand.items():
            if color == BLACK:
                inhand = self.ui.position.inhand['downside']
            else:
                inhand = self.ui.position.inhand['upside']
            for t, n in data.items():
                inhand.put(t.upper(), n)
