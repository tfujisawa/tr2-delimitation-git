import sys

from tree_node import *
from newick_io import *

def list_tip_names(tr, sep=" "):
	return [sep.join(nod.name) for nod in tr.traverse() if nod.is_terminal()]

def unique_count(stream, prop=False):
	taxa_count = {}
	for i, line in enumerate(stream):
		tr = parse_newick(line.rstrip("\n"))
		
		names = list_tip_names(tr)

		#print names
		for name in names:
			if name in taxa_count:
				taxa_count[name] += 1
			else:	
				taxa_count[name] = 1

	if prop:
		print i+1
		for k in taxa_count:
			taxa_count[k] = taxa_count[k]/float(i+1)

	return taxa_count

if __name__=="__main__":
	with open(sys.argv[1], "r") as f:
		print unique_count(f, prop=True)

