#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import argparse
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile')
    parser.add_argument('-s', '--sfen', default=sfen.STARTPOS)
    parser.add_argument('-t', '--theme', default='theme-terminal.json')
    args = parser.parse_args()

    theme_file = os.path.join(os.path.expanduser('~'),
            '.pytk-shogi-replayer', args.theme)
    if not os.path.exists(theme_file):
        theme_file = os.path.join(os.path.dirname(__file__), args.theme)

    theme = theming.Theme(theme_file)
    ui = tkui.UI(theme)

    if args.logfile:
        position, movelog = load_file(args.sfen, args.logfile)
    else:
        movelog = shogi.Movelog()
        position = sfen.decoder(args.sfen)

    player = replayer.Replayer(ui, movelog, position)
    player.init()

    def open_file(filename):
        s = sfen.STARTPOS
        player.position, player.movelog = load_file(s, filename)
        player.init()

    ui.menu.command['open_file'] = open_file

    ui.run()

if __name__ == '__main__':
    main()
