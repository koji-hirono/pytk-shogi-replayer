# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from shogi import Coords, Move, BLACK, WHITE
import copy
import re

"""
.kif = encoding Shift_JIS
.kifu = encoding UTF-8


movelog = {info} move_sep move+

info = 
    '開始日時' sep string
    | '対局日' sep string
    | '終了日時' sep string
    | '棋戦' sep string
    | '戦型' sep string
    | '表題' sep string
    | '持ち時間' sep string
    | '消費時間' sep string
    | '場所' sep string
    | '掲載' sep string
    | '備考' sep string
    | '先手省略名' sep string
    | '後手省略名' sep string
    | '先手' sep string
    | '後手' sep string
    | '下手' sep string
    | '上手' sep string
    | '手合割' sep handicap
    .

move_sep = '手数' '-'+ '指手' '-'+ '消費時間' '-'+ .

move = 
    step [color] dst piece '打' ['(' time ')']
    step [color] (dst | '同') piece ['成'] '(' src ')' ['(' time ')']
    step end_keyword
    | '*' string
    | '&' string
    .

handicap =
    '平手' | '香落ち' | '右香落ち' | '角落ち' | '飛車落ち'
    | '飛香落ち' | '二枚落ち' | '三枚落ち' | '四枚落ち' | '五枚落ち'
    | '左五枚落ち' | '六枚落ち' | '八枚落ち' | '十枚落ち' | 'その他'
    .

color = '▲' | '△' .

piece =
    '歩' | '香' | '桂' | '銀' | '金' | '角' | '飛' | '王' | '玉'
    | 'と' | '成香' | '成桂' | '成銀' | '馬' | '竜' | '龍'
    .

end_keyword =
    '詰み' | '投了' | '切れ負け' | '中断' | '千日手' | '持将棋'
    | '反則負け' | '反則勝ち'
    .

dst = file rank .

src = digit digit .

file = '１' | '２' | '３' | '４' | '５' | '６' | '７' | '８' | '９' .

rank = '一' | '二' | '三' | '四' | '五' | '六' | '七' | '八' | '九' .

time = digit+ ':' digit+ '/' [digit+ ':' digit+ ':' digit+]

sep = ':' | '：' .

comment = Regexp('#.*\n') .

string = Regexp('.*') .


"""

RANKNUM = {
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9
}

PIECE = {
    '歩': 'P',
    '香': 'L',
    '桂': 'N',
    '銀': 'S',
    '金': 'G',
    '角': 'B',
    '飛': 'R',
    '王': 'K',
    '玉': 'K',
    'と': '+P',
    '成香': '+L',
    '成桂': '+N',
    '成銀': '+S',
    '馬': '+B',
    '竜': '+R',
    '龍': '+R'
}

END_KEYWORD = {
    '詰み': 'checkmate',
    '詰': 'checkmate',
    '投了': 'resign',
    '切れ負け': 'timeout',
    '中断': 'suspend',
    '千日手': 'repetition',
    '持将棋': 'impasse',
    '反則負け': 'illegal_move',
    '反則勝ち': 'illegal_prev_move'
}

COLOR = {
    '▲': BLACK,
    '△': WHITE
}

def decoder(f):
    prevdst = None
    color = BLACK
    for line in f:
        if isinstance(line, bytes):
            try:
                line = line.decode('utf-8')
            except:
                try:
                    line = line.decode('shift_jis')
                except:
                    raise
        line = line.strip()
        m = re.match(r'\s*\d+\s+(.+?)\s*(\(\s*\d+:\d+\s*/\s*(\d+:\d+:\d+)?\s*\))?\s*$', line)
        if not m:
            # print('unmatch {}'.format(line))
            continue
        line = m.group(1)
        line = line.strip()
        if line in END_KEYWORD:
            # print('line = "{}"'.format(line))
            break
        # print('line = "{}"'.format(line))
        if line[0] == '同':
            dst = copy.deepcopy(prevdst)
            if line[1].isspace():
                piece_pos = 2
            else:
                piece_pos = 1
        else:
            dst = Coords(line[0], RANKNUM[line[1]])
            piece_pos = 2
        # print('dst file = {} rank = {}'.format(dst.file, dst.rank))

        m = re.search(r'(成|打)?\((\d)(\d)\)', line)
        if m and m.group(1) != '打':
            src = Coords(m.group(2), m.group(3))
            # print('src file = {} rank = {}'.format(src.file, src.rank))
            if m.group(1) == '成':
                promote = True
            else:
                promote = False
            piece = None
        else:
            src = None
            promote = None
            piece = PIECE[line[piece_pos]]
        # print('color = {}'.format(color))
        # print('piece = {}'.format(piece))
        yield Move(color, dst, src, piece, promote)
        if color == BLACK:
            color = WHITE
        else:
            color = BLACK
        prevdst = dst
