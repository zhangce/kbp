#! /usr/bin/env python

import sys, json

f = open(sys.argv[1], 'w')

for row in sys.stdin:
	f.write(row)

f.close()