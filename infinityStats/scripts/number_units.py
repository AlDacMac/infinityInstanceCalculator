#!/usr/bin/env python
import simplejson as json
import sys
from collections import OrderedDict

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

if len(sys.argv) != 3:
	print "Usage: number_units input_file start_index"
	sys.exit(1)

filename = sys.argv[1]
index = int(sys.argv[2])

print "Reading from: " + filename
with open(filename, 'r') as f:
     data = json.load(f, object_pairs_hook=OrderedDict)
     
#print data


for i in range(len(data)):
	index = index+1;
	data[i].update({"id":index})


print "Writing to: " + filename
with open(filename, 'w') as outfile:
    json.dump(data, outfile, indent=2, separators=(',', ': '))
    

