# -*- coding: utf-8 -*-

from shogi import Coords, BLACK, WHITE

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
                                    self.ui.piece_type['p'],
                                    lastmove.src.rank - 1,
                                    self.position.nfiles - lastmove.src.file)
                    if lastmove.dst:
                        if lastmove.dst.file == file and lastmove.dst.rank == rank:
                            self.ui.position.square.set_style(
                                    self.ui.piece_type['p'],
                                    lastmove.dst.rank - 1,
                                    self.position.nfiles - lastmove.dst.file,
                                    stipple='gray75')
                if piece:
                    self.ui.position.square.put(self.ui.piece_type[piece], row, col)
        for color, data in self.position.inhand.items():
            if color == BLACK:
                inhand = self.ui.position.inhand[1]
            else:
                inhand = self.ui.position.inhand[0]
            for t, n in data.items():
                if color == BLACK:
                    sym = t.upper()
                else:
                    sym = t.lower()
                inhand.clear(self.ui.piece_type[sym])
                if n != 0:
                    inhand.put(self.ui.piece_type[sym], n)
