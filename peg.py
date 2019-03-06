# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import types
import re


class Sequence(object):

    def __init__(self, *exprs):
        self.exprs = exprs

    def parse(self, parser):
        ts = []
        pos = parser.pos
        for expr in self.exprs:
            accepted, t = expr.parse(parser)
            if not accepted:
                parser.pos = pos
                return False, ts
            ts.append(t)
        return True, ts


class OrderdChoice(object):

    def __init__(self, *exprs):
        self.exprs = exprs

    def parse(self, parser):
        pos = parser.pos
        for expr in self.exprs:
            accepted, t = expr.parse(parser)
            if accepted:
                return True, t
            else:
                parser.pos = pos
        return False, None


class ZeroOrMore(object):

    def __init__(self, expr):
        self.expr = expr

    def parse(self, parser):
        ts = []
        while True:
            pos = parser.pos
            accepted, t = self.expr.parse(parser)
            if not accepted:
                parser.pos = pos
                break
            ts.append(t)
        return True, ts


class OneOrMore(object):

    def __init__(self, expr):
        self.expr = expr

    def parse(self, parser):
        ts = []
        while True:
            pos = parser.pos
            accepted, t = self.expr.parse(parser)
            if not accepted:
                parser.pos = pos
                break
            ts.append(t)
        if len(ts) == 0:
            return False, None
        return True, ts


class Optional(object):

    def __init__(self, expr):
        self.expr = expr

    def parse(self, parser):
        pos = parser.pos
        accepted, t = self.expr.parse(parser)
        if accepted:
            return True, t
        else:
            parser.pos = pos
            return True, None


class And(object):

    def __init__(self, expr):
        self.expr = expr

    def parse(self, parser):
        pos = parser.pos
        accepted, t = self.expr.parse(parser)
        parser.pos = pos
        if accepted:
            return True, None
        else:
            return False, None


class Not(object):

    def __init__(self, expr):
        self.expr = expr

    def parse(self, parser):
        pos = parser.pos
        accepted, t = self.expr.parse(parser)
        parser.pos = pos
        if accepted:
            return False, None
        else:
            return True, None


class Literal(object):

    def __init__(self, text):
        self.text = text

    def parse(self, parser):
        parser.skip_space()
        n = len(self.text)
        if parser.text[parser.pos:parser.pos+n] == self.text:
            parser.pos += n
            return True, self.text
        else:
            return False, None


class Regexp(object):

    def __init__(self, text):
        self.ptn = re.compile(text)

    def parse(self, parser):
        parser.skip_space()
        m = self.ptn.match(parser.text, parser.pos)
        if m:
            matched = m.group()
            parser.pos += len(matched)
            return True, matched
        else:
            return False, None


class Rule(object):

    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr

    def parse(self, parser):
        pos = parser.pos
        memo = parser.get_memo(pos, self.name)
        if memo:
            t, next_pos = memo
            parser.pos = next_pos
            return True, t
        accepted, t = self.expr.parse(parser)
        if not accepted:
            return False, t
        sem = parser.semantics
        if sem:
            if hasattr(sem, self.name):
                f = getattr(sem, self.name)
                t = f(t)
            elif hasattr(sem, '_default'):
                f = getattr(sem, '_default')
                t = f(t)
            parser.set_memo(pos, self.name, (t, parser.pos))
        return accepted, t


class Parser(object):

    def __init__(self, text, semantics=None):
        self.text = text
        self.pos = 0
        self.memo = {}
        self.semantics = semantics

    def get_memo(self, pos, name):
        if pos in self.memo:
            if name in self.memo[pos]:
                return self.memo[pos][name]
        return None

    def set_memo(self, pos, name, memo):
        self.memo.setdefault(pos, {})
        self.memo[pos][name] = memo

    def skip_space(self):
        pos = self.pos
        for c in self.text[pos:]:
            if not c.isspace():
                break
            pos += 1
        self.pos = pos


class GrammarBuilder(object):

    def __init__(self):
        self.cache = {}

    def build(self, expr):
        if isinstance(expr, types.FunctionType):
            name = expr.__name__
            if name in self.cache:
                return self.cache[name]
            else:
                r = Rule(name)
                self.cache[name] = r
                r.expr = self.build(expr())
                return r
        elif isinstance(expr, type('')):
            return Literal(expr)
        elif isinstance(expr, tuple):
            return Sequence(*(self.build(e) for e in expr))
        elif isinstance(expr, list):
            return OrderdChoice(*(self.build(e) for e in expr))
        else:
            return expr

    def repeat0(self, *exprs):
        if len(exprs) == 1:
            expr = self.build(exprs[0])
        else:
            expr = self.build(exprs)
        return ZeroOrMore(expr)

    def repeat1(self, *exprs):
        if len(exprs) == 1:
            expr = self.build(exprs[0])
        else:
            expr = self.build(exprs)
        return OneOrMore(expr)

    def opt(self, *exprs):
        if len(exprs) == 1:
            expr = self.build(exprs[0])
        else:
            expr = self.build(exprs)
        return Optional(expr)

    def absent(self, *exprs):
        if len(exprs) == 1:
            expr = self.build(exprs[0])
        else:
            expr = self.build(exprs)
        return Not(expr)

    def present(self, *exprs):
        if len(exprs) == 1:
            expr = self.build(exprs[0])
        else:
            expr = self.build(exprs)
        return And(expr)

    def regexp(self, text):
        return Regexp(text)
