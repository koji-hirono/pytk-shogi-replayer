# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import os

class Theme(object):

    def __init__(self, filename):
        self.filename = filename
        self.dir = os.path.dirname(self.filename)
        with open(filename, 'r') as f:
            self.config = json.load(f)

