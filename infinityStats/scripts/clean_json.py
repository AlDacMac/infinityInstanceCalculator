#!/usr/bin/env python
import simplejson as json
import sys
from collections import OrderedDict
import codecs

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
'comment', 'id', 'obsolete', 'army', 'army_id', 'sectorial',
'isc', 'legacy_isc', 'name', 'legacy_name', 'abbr', 'units', 'image',
'optionSpecific', 'type', 'classification', 'imp', 'irr', 'cube', 'hackable', 'mov', 'cc', 'bs', 'ph', 'wip', 'arm',
'bts', 'w', 'wtype', 's', 'ava', 'sharedAva', 'code', 'legacy_code', 'codename', 'cost', 'swc', 'profile', 'option', 'spec', 'bsw',
'ccw', 'independent', 'profiles', 'skills', 'childs', 'hide', 'add', 'title', 'note', 'notes'
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
with codecs.open(filename, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, indent=2, separators=(',', ': '), ensure_ascii=False)
    outfile.write('\n')


