#! /usr/bin/env python

import sys, json

"""
Dummy extractor to simply spit out the input query as a JSON file.

The filename must be passed as the only argument to this script.
"""

f = open(sys.argv[1], 'a')
for row in sys.stdin:
	f.write(row)
f.close()