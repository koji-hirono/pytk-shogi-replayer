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
import kif
import shogi
import replayer


def load_file(movelog, position, s, logfile):
    position.load(sfen.decoder(s))
    if logfile.lower().endswith('.usi'):
        with open(logfile, 'r') as f:
            movelog.load(psn.decoder(f))
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

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        logfile = sys.argv[1]
    else:
        logfile = None
    if len(sys.argv) >= 3:
        s = sys.argv[2]
    else:
        s = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -'

    theme = theming.Theme('theme-terminal.json')
    ui = tkui.UI(theme)
    position = shogi.Position()
    movelog = shogi.Movelog()

    if logfile:
        load_file(movelog, position, s, logfile)
    else:
        position.load(sfen.decoder(s))

    player = replayer.Replayer(ui, movelog, position)
    player.init()

    def open_file(filename):
        s = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -'
        load_file(player.movelog, player.position, s, filename)
        player.init()

    ui.menu.command['open_file'] = open_file

    ui.run()
