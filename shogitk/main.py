#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import argparse
import shogitk.tkui as tkui
import shogitk.theming as theming
import shogitk.sfen as sfen
import shogitk.shogi as shogi
import shogitk.replayer as replayer


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
        position, movelog = replayer.load_file(args.sfen, args.logfile)
    else:
        movelog = shogi.Movelog()
        position = sfen.decoder(args.sfen)

    player = replayer.Replayer(ui, movelog, position)
    player.init()

    ui.run()

if __name__ == '__main__':
    main()
