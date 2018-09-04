#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import tkui
import theming
import sfen
import psn
import mobakif
import shogi

def update(position, ui):
    for i, row in enumerate(position.square):
        for j, t in enumerate(row):
            ui.position.square.take(i, j)
            if t != '':
                ui.position.square.put(ui.piece_type[t], i, j)
    for color, data in position.inhand.items():
        if color == 'black':
            inhand = ui.position.inhand[1]
        else:
            inhand = ui.position.inhand[0]
        for t, n in data.items():
            if color == 'black':
                sym = t.upper()
            else:
                sym = t.lower()
            inhand.clear(ui.piece_type[sym])
            if n != 0:
                inhand.put(ui.piece_type[sym], n)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} LOGFILE'.format(__file__))
        sys.exit(1)
    logfile = sys.argv[1]

    theme = theming.Theme('theme-terminal.json')
    ui = tkui.UI(theme)
    position = shogi.Position()
    movelog = shogi.Movelog()

    s = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -'
    position.load(sfen.decoder(s))

    if logfile.endswith('.usi'):
        with open(logfile, 'r') as f:
            movelog.load(psn.decoder(f))
            movelog.normalize(position)
    elif logfile.endswith('.kif'):
        with open(logfile, 'r') as f:
            movelog.load(mobakif.decoder(f))
            movelog.normalize(position)

    movelog.goto(position, 0)
    step = position.step - 1
    ui.control.curr_v.set(step)

    ui.movelog.load(movelog.data)

    def move_first():
        movelog.goto(position, 0)
        step = position.step - 1
        ui.control.curr_v.set(step)
        item = ui.movelog.tree.get_children()[step]
        ui.movelog.tree.selection_set(item)
        ui.movelog.tree.focus(item)
        ui.movelog.tree.see(item)
        update(position, ui)

    def move_last():
        movelog.goto(position, len(movelog.data) - 1)
        step = position.step - 1
        ui.control.curr_v.set(step)
        item = ui.movelog.tree.get_children()[step]
        ui.movelog.tree.selection_set(item)
        ui.movelog.tree.focus(item)
        ui.movelog.tree.see(item)
        update(position, ui)

    def move_back():
        movelog.back(position, 1)
        step = position.step - 1
        ui.control.curr_v.set(step)
        item = ui.movelog.tree.get_children()[step]
        ui.movelog.tree.selection_set(item)
        ui.movelog.tree.focus(item)
        ui.movelog.tree.see(item)
        update(position, ui)

    def move_forward():
        movelog.forward(position, 1)
        step = position.step - 1
        ui.control.curr_v.set(step)
        item = ui.movelog.tree.get_children()[step]
        ui.movelog.tree.selection_set(item)
        ui.movelog.tree.focus(item)
        ui.movelog.tree.see(item)
        update(position, ui)

    def move_goto(event):
        sym = ui.movelog.tree.focus()
        step = ui.movelog.tree.index(sym)
        movelog.goto(position, step)
        ui.control.curr_v.set(step)
        update(position, ui)

    ui.control.first.configure(command=move_first)
    ui.control.last.configure(command=move_last)
    ui.control.prev1.configure(command=move_back)
    ui.control.next1.configure(command=move_forward)
    ui.movelog.tree.bind('<ButtonRelease-1>', move_goto)

    update(position, ui)

    ui.run()
