# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

class Theme(object):

    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.config = json.load(f)

