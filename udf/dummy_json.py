#! /usr/bin/env python

import sys, json

f = open('/lfs/local/0/msushkov/deepdive/app/kbp/udf/string_library_test_large.json', 'a')

for row in sys.stdin:
	f.write(row)

f.close()