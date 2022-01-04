# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    import tkinter as tk
    import tkinter.font as tkfont
    import tkinter.ttk as ttk
    from tkinter import filedialog
except:
    import Tkinter as tk
    import tkFont as tkfont
    import ttk
    import tkFileDialog as filedialog
import os
from PIL import ImageTk


class Square(tk.Frame):
    def __init__(self, parent, theme, piece_type):
        tk.Frame.__init__(self, parent)
        self.piece_type = piece_type
        imgpath = os.path.join(theme.dir, 'images')
        self.bg_img = ImageTk.PhotoImage(
                file=os.path.join(theme.dir, 'images',
                    theme.config['board']['background']))
        self.sq_img = ImageTk.PhotoImage(
                file=os.path.join(theme.dir, 'images',
                    theme.config['board']['square']))
        w = self.bg_img.width()
        h = self.bg_img.height()
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.back = self.canvas.create_image(0, 0, anchor='nw', image=self.bg_img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.sq_img)
        self.canvas.grid(row=1, column=0)
        self.padx = theme.config['board']['padding']['x']
        self.pady = theme.config['board']['padding']['y']
        self.file = theme.config['axis']['file']
        self.rank = theme.config['axis']['rank']
        ax_frame = tk.Frame(self, padx=self.padx, pady=0)
        ax_frame.grid(row=0, column=0, sticky='esnw')
        for i, text in enumerate(reversed(self.file)):
            ax = tk.Label(ax_frame, text=text)
            ax.grid(row=0, column=i, sticky='esnw')
            ax_frame.columnconfigure(i, weight=1)
        ay_frame = tk.Frame(self, padx=0, pady=self.pady)
        ay_frame.grid(row=1, column=1, sticky='esnw')
        for i, text in enumerate(self.rank):
            ay = tk.Label(ay_frame, text=text)
            ay.grid(row=i, column=0, sticky='esnw')
            ay_frame.rowconfigure(i, weight=1)

    def put(self, side, piece, row, col):
        img = self.piece_type[side][piece].image
        x = self.padx + img.width() * col
        y = self.pady + img.height() * row
        tag = '{},{}'.format(row, col)
        self.canvas.create_image(x, y, tag=tag, anchor='nw', image=img)

    def take(self, row, col):
        tag = '{},{}'.format(row, col)
        self.canvas.delete(tag)

    def set_style(self, row, col, fill='lightblue', stipple='gray50'):
        img = self.piece_type['upside']['P'].image
        x = self.padx + img.width() * col
        y = self.pady + img.height() * row
        tag = '{},{} style'.format(row, col)
        r = self.canvas.create_rectangle(x, y, x + img.width(),
                y + img.height(), tag=tag, fill=fill, stipple=stipple)
        self.canvas.tag_lower(r)
        self.canvas.tag_lower(self.back)

    def clear_style(self, row, col):
        tag = '{},{} style'.format(row, col)
        self.canvas.delete(tag)


class InHand(tk.Frame):
    def __init__(self, parent, theme, piece_type):
        tk.Frame.__init__(self, parent)
        anchor='nw'
        self.image = {}
        self.count = {}
        w = 0
        h = 0
        for p in piece_type:
            h += p.image.height()
            if p.image.width() > w:
                w = p.image.width()
        w *= 2
        self.canvas = tk.Canvas(self, width=w, height=h)
        self.back = self.canvas.create_rectangle(0, 0, w, h, fill='#eeeebb')
        self.canvas.grid(row=0, column=0)
        for i, p in enumerate(piece_type):
            x = 0
            y = p.image.height() * i
            self.image[p.name] = self.canvas.create_image(x, y,
                    anchor=anchor, image=p.image)
            x += p.image.width()
            self.count[p.name] = self.canvas.create_text(x, y,
                    anchor=anchor, font=('', 16), text=str(0))
            self.canvas.tag_lower(self.count[p.name], self.back)
            self.canvas.tag_lower(self.image[p.name], self.back)

    def put(self, piece, n):
        if piece not in self.image:
            return
        self.canvas.itemconfigure(self.count[piece], text=str(n))
        if n > 0:
            self.canvas.tag_raise(self.count[piece], self.back)
            self.canvas.tag_raise(self.image[piece], self.back)
        else:
            self.canvas.tag_lower(self.count[piece], self.back)
            self.canvas.tag_lower(self.image[piece], self.back)

class Position(tk.Frame):
    def __init__(self, parent, theme, piece_type):
        tk.Frame.__init__(self, parent)
        self.square = Square(self, theme, piece_type)
        self.inhand = {
            'upside':InHand(self, theme,
                [piece_type['upside'][p] for p in reversed('RBGSNLP')]),
            'downside':InHand(self, theme,
                [piece_type['downside'][p] for p in 'RBGSNLP'])
        }
        self.inhand['upside'].grid(row=0, column=0, padx=5, pady=5, sticky='n')
        self.square.grid(row=0, column=1, padx=5, pady=5, sticky='ns')
        self.inhand['downside'].grid(row=0, column=2, padx=5, pady=5, sticky='s')

def move_format(m, theme):
    if theme.config['move']['style'] == 'western':
        s = theme.config['piece']['name'][m.piece.upper()]
        if m.isdrop():
            s += theme.config['piece']['drop']
        elif m.capture is not None:
            s += theme.config['axis']['file'][m.src.file - 1]
            s += theme.config['axis']['rank'][m.src.rank - 1]
            s += 'x'
        else:
            s += theme.config['axis']['file'][m.src.file - 1]
            s += theme.config['axis']['rank'][m.src.rank - 1]
            s += '-'
        s += theme.config['axis']['file'][m.dst.file - 1]
        s += theme.config['axis']['rank'][m.dst.rank - 1]
        if m.ispromote():
            s += theme.config['piece']['promote']
    else:
        s = theme.config['color'][m.color]
        s += theme.config['axis']['file'][m.dst.file - 1]
        s += theme.config['axis']['rank'][m.dst.rank - 1]
        s += theme.config['piece']['name'][m.piece.upper()]
        if m.ispromote():
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

    def clear(self):
        items = self.tree.get_children()
        self.tree.delete(*items)

    def set_step(self, step):
        items = self.tree.get_children()
        if step < len(items):
            item = items[step]
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)

    def get_step(self):
        sym = self.tree.focus()
        return self.tree.index(sym)

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

class Menu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        filemenu = tk.Menu(self, tearoff=0)
        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=parent.quit)
        self.add_cascade(label='File', menu=filemenu)
        self.command = {}

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            if 'open_file' in self.command:
                self.command['open_file'](filename)

class PieceType(object):
    def __init__(self, name, image):
        self.name = name
        self.image = image

class UI(object):
    def __init__(self, theme):
        self.root = tk.Tk()
        self.root.title('shogi')
        self.piece_type = {}
        for side, piece in theme.config['piece']['image'].items():
            self.piece_type[side] = {}
            for name, file in piece.items():
                self.piece_type[side][name] = PieceType(name, ImageTk.PhotoImage(
                        file=os.path.join(theme.dir, 'images', file)))
        self.position = Position(self.root, theme, self.piece_type)
        self.movelog = Movelog(self.root, theme)
        self.control = Control(self.root, theme)
        self.position.grid(row=0, column=0)
        self.movelog.grid(row=0, column=1, sticky='ns')
        self.control.grid(row=1, column=0)
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

    def run(self):
        self.root.mainloop()
