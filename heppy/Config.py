#!/usr/bin/env python

import os
import sys
import json
import collections

from pprint import pprint

# http://stackoverflow.com/questions/10703858
def merge_dict(d1, d2):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for k,v2 in d2.items():
        v1 = d1.get(k) # returns None if v1 has no value for this key
        if (isinstance(v1, collections.Mapping)
        and isinstance(v2, collections.Mapping)):
            merge_dict(v1, v2)
        else:
            d1[k] = v2

class Config(dict):
    def __init__(self, filename):
        with open(self.find(filename)) as file:
            self.merge(json.load(file))

    def merge(self, data):
        merge_dict(self, data)

    def find(self, filename):
        if os.path.isfile(filename):
            return filename

        command = sys.argv[0]
        if '/' != command[0]:
            command = os.path.normpath(os.path.join(os.getcwd(), command))
        path = os.path.join(os.path.dirname(os.path.dirname(command)), 'etc', filename)
        if os.path.isfile(path):
            return path

        ext = os.path.splitext(filename)[1]

        if not ext:
            return self.find(filename + '.json')
        else:
            return os.path.join('/etc/heppy', filename)
