#!/usr/bin/env python
import simplejson as json
import sys
from collections import OrderedDict
import codecs

if len(sys.argv) != 2:
    print "Usage: %s input_file" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]

print "Reading from: " + filename
with open(filename, 'r') as f:
     data = json.load(f, object_pairs_hook=OrderedDict)
     
#print data


for i in range(len(data)):
    if data[i].has_key("legacy_name"):
        del data[i]["legacy_name"]

    if data[i].has_key("legacy_isc"):
        del data[i]["legacy_isc"]

    if data[i].has_key("childs"):
        index = 1;
        for j in range(len(data[i]["childs"])):
            if data[i]["childs"][j].has_key("legacy_code"):
                del data[i]["childs"][j]["legacy_code"] 
			

print "Writing to: " + filename
with codecs.open(filename, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, indent=2, separators=(',', ': '), ensure_ascii=False)
