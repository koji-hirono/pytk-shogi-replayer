#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import tkui
import theming
import sfen
import usikif
import mobakif
import kif
import ki2
import psn
import shogi
import replayer


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

    if logfile:
        position, movelog = load_file(s, logfile)
    else:
        movelog = shogi.Movelog()
        position = sfen.decoder(s)

    player = replayer.Replayer(ui, movelog, position)
    player.init()

    def open_file(filename):
        s = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -'
        player.position, player.movelog = load_file(s, filename)
        player.init()

    ui.menu.command['open_file'] = open_file

    ui.run()
