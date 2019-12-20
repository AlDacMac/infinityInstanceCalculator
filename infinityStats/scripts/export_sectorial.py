import simplejson as json
import sys
from collections import OrderedDict

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

if len(sys.argv) != 2:
	print "Usage: export_sectorial input_file "
	sys.exit(1)

filename = sys.argv[1]

print "Reading from: " + filename
with open(filename, 'r') as f:
     data = json.load(f, object_pairs_hook=OrderedDict)
     
#print data

unitlist = json.loads("[]")

for i in range(len(data)):
	unit = dict();
	unit["comment"] = data[i]["isc"]
	unit["id"] = data[i]["id"]
	unitlist.append(unit)

filename = "sectorial_data.json"

print "Writing to: " + filename
with open(filename, 'w') as outfile:
    json.dump(unitlist, outfile, indent=2, separators=(',', ': '))
    

