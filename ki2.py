# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from peg import GrammarBuilder, Parser
from shogi import Coords, Move
from shogi import BLACK, WHITE
from shogi import RIGHT, LEFT, VERTICAL
from shogi import UPWARD, DOWNWARD, HORIZONTAL
from shogi import DROP, PROMOTE, NOTPROMOTE
import sys


def grammar():
    g = GrammarBuilder()

    def piece():
        return ['歩', '香', '桂', '銀', '金', '角', '飛', '王', '玉',
                'と', '成香', '成桂', '成銀', '馬', '竜', '龍']

    def rank():
        return ['一', '二', '三', '四', '五', '六', '七', '八', '九']

    def file():
        return ['１', '２', '３', '４', '５', '６', '７', '８', '９']

    def relative():
        return ['右', '左', '直']

    def movement():
        return ['上', '引', '寄']

    def modifier():
        return ['打', '成', '不成']

    def any_string():
        return g.regexp(r'[^\n]*')

    def sep():
        return [':', '：']

    def info_keyword():
        return ['開始日時', '対局日', '終了日時', '棋戦', '表題', '戦型',
                '持ち時間', '消費時間', '場所', '掲載', '備考', '先手省略名',
                '後手省略名', '先手', '後手', '下手', '上手', '手合割']

    def info():
        return info_keyword, sep, any_string

    def result():
        return 'まで', any_string

    def dst():
        return [(file, rank), '同']

    def color():
        return ['▲', '△']

    def comment():
        return '#', any_string

    def user_comment():
        return '*', any_string

    def bookmark():
        return '&', any_string

    def move():
        return (g.opt(color), dst, piece, g.opt(relative),
                g.opt(movement), g.opt(modifier))

    def movelog():
        return (g.repeat0([info, comment]),
                g.repeat1([move, user_comment, bookmark]),
                g.opt(result))

    return g.build(movelog)


class Semantics(object):

    def color(self, t):
        return {'▲':BLACK, '△':WHITE}[t]

    def file(self, t):
        return {'１':1, '２':2, '３':3, '４':4, '５':5,
                '６':6, '７':7, '８':8, '９':9}[t]

    def rank(self, t):
        return {'一':1, '二':2, '三':3, '四':4, '五':5,
                '六':6, '七':7, '八':8, '九':9}[t]

    def piece(self, t):
        return {'歩':'P', '香':'L', '桂':'N', '銀':'S', '金':'G',
                '角':'B', '飛':'R', '王':'K', '玉':'K', 'と':'+P',
                '成香':'+L', '成桂':'+N', '成銀':'+S', '馬':'+B',
                '竜':'+R', '龍':'+R'}[t]

    def relative(self, t):
        return {'右':RIGHT, '左':LEFT, '直':VERTICAL}[t]

    def movement(self, t):
        return {'上':UPWARD, '引':DOWNWARD, '寄':HORIZONTAL}[t]

    def modifier(self, t):
        return {'打':DROP, '成':PROMOTE, '不成':NOTPROMOTE}[t]

    def dst(self, t):
        if isinstance(t, list):
            return Coords(t[0], t[1])
        else:
            return 'same'

    def move(self, t):
        return Move(t[0], t[1], piece=t[2], relative=t[3], movement=t[4],
                modifier=t[5])

    def movelog(self, t):
        return t[1]


def decoder(f):
    g = grammar()
    s = f.read()
    if isinstance(s, bytes):
        try:
            s = s.decode('utf-8')
        except:
            s = s.decode('shift_jis')
    parser = Parser(s, semantics=Semantics())
    accepted, t = g.parse(parser)
    return t
