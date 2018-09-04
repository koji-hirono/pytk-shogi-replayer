# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    import tkinter as tk
    import tkinter.font as tkfont
    import tkinter.ttk as ttk
except:
    import Tkinter as tk
    import tkFont as tkfont
    import ttk
from PIL import ImageTk


class Square(tk.Frame):
    def __init__(self, parent, theme):
        tk.Frame.__init__(self, parent)
        self.bg_img = ImageTk.PhotoImage(
                file='images/' + theme.config['board']['background'])
        self.sq_img = ImageTk.PhotoImage(
                file='images/' + theme.config['board']['square'])
        w = self.bg_img.width()
        h = self.bg_img.height()
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.sq_img)
        self.canvas.grid(row=1, column=0)
        self.padx = theme.config['board']['padding']['x']
        self.pady = theme.config['board']['padding']['y']
        self.file = theme.config['axis']['file']
        self.rank = theme.config['axis']['rank']
        # axis_w = (w - self.padx * 2) / len(self.file)

    def put(self, piece, row, col):
        img = piece['image']
        x = self.padx + img.width() * col
        y = self.pady + img.height() * row
        tag = '{},{}'.format(row, col)
        self.canvas.create_image(x, y, tag=tag, anchor='nw', image=img)

    def take(self, row, col):
        tag = '{},{}'.format(row, col)
        self.canvas.delete(tag)

class InHand(tk.Frame):
    def __init__(self, parent, theme):
        tk.Frame.__init__(self, parent)
        w = 90
        h = 370
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.canvas.create_rectangle(0, 0, w, h, fill='#eeeebb')
        self.canvas.grid(row=0, column=0)

    def put(self, piece, n):
        P_W = {
            'R': 0, 'B': 1, 'G': 2, 'S': 3, 'N': 4, 'L': 5, 'P': 6,
            'r': 6, 'b': 5, 'g': 4, 's': 3, 'n': 2, 'l': 1, 'p': 0
        }
        img = piece['image']
        x = 5
        y = (img.height() + 0) * P_W[piece['name']]
        tag = '{}'.format(piece['name'])
        self.canvas.create_image(x, y, tag=tag, anchor='nw', image=img)
        x += img.width() + 5
        tag = '{} count'.format(piece['name'])
        self.canvas.create_text(x, y, tag=tag, anchor='nw', font=('', 16),
                text=str(n))

    def clear(self, piece):
        tag = '{}'.format(piece['name'])
        self.canvas.delete(tag)
        tag = '{} count'.format(piece['name'])
        self.canvas.delete(tag)

class Position(tk.Frame):
    def __init__(self, parent, theme):
        tk.Frame.__init__(self, parent)
        self.square = Square(self, theme)
        self.inhand = [InHand(self, theme), InHand(self, theme)]
        self.inhand[0].grid(row=0, column=0, padx=5, pady=5, sticky='n')
        self.square.grid(row=0, column=1, padx=5, pady=5, sticky='ns')
        self.inhand[1].grid(row=0, column=2, padx=5, pady=5, sticky='s')

def move_format(m, theme):
    s = theme.config['color'][m.color]
    s += theme.config['axis']['file'][m.dst.file - 1]
    s += theme.config['axis']['rank'][m.dst.rank - 1]
    s += theme.config['piece']['name'][m.piece.upper()]
    if m.promote:
        s += theme.config['piece']['promote']
    if m.src:
        s += '({}{})'.format(m.src.file, m.src.rank)
    else:
        s += theme.config['piece']['drop']
    return s

class Movelog(tk.Frame):
    def __init__(self, parent, theme):
        tk.Frame.__init__(self, parent)
        self.theme = theme
        self.tree = ttk.Treeview(self, show='headings', columns=(0, 1))
        self.tree.column(0, width=40)
        self.tree.column(1, width=140)
        self.tree.heading(0, text='#', anchor='w')
        self.tree.heading(1, text='Move', anchor='w')
        self.yscroll = ttk.Scrollbar(self, orient='vertical',
                command=self.tree.yview)
        self.xscroll = ttk.Scrollbar(self, orient='horizontal',
                command=self.tree.xview)
        self.tree.config(yscrollcommand=self.yscroll.set,
                xscrollcommand=self.xscroll.set)
        self.tree.grid(row=0, column=0)
        self.yscroll.grid(row=0, column=1, sticky='ns')
        self.xscroll.grid(row=1, column=0, sticky='ew')

    def load(self, logs):
        for i, m in enumerate(logs):
            if m:
                s = move_format(m, self.theme)
            else:
                s = 'Initial'
            self.tree.insert('', 'end', values=(i, s))

class Control(tk.Frame):
    def __init__(self, parent, theme):
        tk.Frame.__init__(self, parent)
        font = ('', 14)
        self.curr_v = tk.StringVar()
        self.first = tk.Button(self, text='|<', font=font)
        self.prev1 = tk.Button(self, text='<', font=font)
        self.curr = tk.Label(self, textvariable=self.curr_v,
                font=font, bg='white')
        self.next1 = tk.Button(self, text='>', font=font)
        self.last = tk.Button(self, text='>|', font=font)
        self.toggle = tk.Button(self, text='()', font=font)
        self.first.grid(row=0, column=0)
        self.prev1.grid(row=0, column=1)
        self.curr.grid(row=0, column=2)
        self.next1.grid(row=0, column=3)
        self.last.grid(row=0, column=4)
        self.toggle.grid(row=0, column=5)

class UI(object):
    def __init__(self, theme):
        self.root = tk.Tk()
        self.root.title('shogi')
        self.piece_type = {}
        for name, file in theme.config['piece']['image'].items():
            self.piece_type[name] = {
                'name': name,
                'image': ImageTk.PhotoImage(file='images/'+file)
            }
        self.position = Position(self.root, theme)
        self.movelog = Movelog(self.root, theme)
        self.control = Control(self.root, theme)
        self.position.grid(row=0, column=0)
        self.movelog.grid(row=0, column=1, sticky='ns')
        self.control.grid(row=1, column=0)

    def run(self):
        self.root.mainloop()
