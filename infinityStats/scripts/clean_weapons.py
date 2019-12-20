#!/usr/bin/env python
import simplejson as json
import sys
from collections import OrderedDict

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

if len(sys.argv) != 2:
	print "Usage: clean_json input_file"
	sys.exit(1)

filename = sys.argv[1]

print "Reading from: " + filename
with open(filename, 'r') as f:
     data = json.load(f)
     
#print data

sort_order = [
'name', 'mode', 'alt_profile', 'burst', 'ammo', 'damage', 'short_dist', 'short_mod', 'medium_dist', 'medium_mod', 
'long_dist', 'long_mod', 'max_dist', 'max_mod', 'attr', 'cc', 'template', 'suppressive', 'uses', 'note'
]



def unitsort(obj):
	if isinstance(obj, list):
		for i in range(len(obj)):
			obj[i] = unitsort(obj[i])
		return obj
	elif isinstance(obj, dict):
		for i in range(len(obj)):
			obj[obj.keys()[i]] = unitsort(obj.values()[i])
		obj =  OrderedDict(sorted(obj.iteritems(), key=lambda (k, v): sort_order.index(k)))
		return obj
	else:
		return obj

#json_ordered = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order.index(k)))
#                    for item in data]

#json_ordered = unitsort(data)

data = unitsort(data)

print "Writing to: " + filename
with open(filename, 'w') as outfile:
    json.dump(data, outfile, indent=2, separators=(',', ': '))
    outfile.write('\n')
    

