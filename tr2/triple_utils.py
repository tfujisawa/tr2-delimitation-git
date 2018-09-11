import sys
import itertools

from tree_node import *
from rooted_triple import *
from newick_io import *

#count the number of triplet topology from a file of multiple trees
def count_triples(f, num_tree="ALL", keep_topology=False):
	triple_count = {}

	if num_tree != "ALL" and type(num_tree) == int:	#use only first N lines, if num_tree is int
		f = itertools.islice(f, num_tree)

	for i, line in enumerate(f):
		tr = parse_newick(line.rstrip("\n"))
		for trpl in RootedTriple.triples_from_tree(tr):
	
			if trpl.members() in triple_count:
				if trpl.topology() in triple_count[trpl.members()]:
					triple_count[trpl.members()][trpl.topology()] += 1
				else:
					triple_count[trpl.members()][trpl.topology()] = 1
			else:
				triple_count[trpl.members()] = {trpl.topology():1}
	print "%d trees read." % (i+1)

	if not keep_topology:
		for k, v in triple_count.items():	#replace dictionary with list of counts
			triple_count[k] = triple_count[k].values()
			if len(triple_count[k]) < 3:	#if length of count is smaller than 3, append 0's
				triple_count[k].extend([0]*(3-len(triple_count[k])%3))	

	return triple_count

#categorize triplets into "within"/"between" groups based on association table
def categorize_triples(triples, assocs, alt_only=False):
	for trpl in triples:
		isexist = [tip in assocs for tip in trpl]
		if not all(isexist):
			#pass	#???			
			yield None
		else:
			tipsp = [assocs[tip] for tip in trpl]
			if tipsp[1:] == tipsp[:-1]:	#if all equal, "within" species category
				#yield "NULL"				
				if alt_only:
					yield None
				else:
					yield "NULL"
			else:	#else, "between" species category, but need to handle 2 different "betweeen"???
				yield "ALT"

if __name__=="__main__":
	with open(sys.argv[1]) as f:
		triple_count = count_triples(f)
	for i, k in enumerate(triple_count):
		print i+1, k, triple_count[k]

	
	tip_group = {}
	with open(sys.argv[2]) as f:
		for line in f:
			l = line.rstrip("\n").split("\t")
			tip_group[l[0]] = l[1]
	print tip_group

	for t, cat in zip(triple_count, categorize_triples(triple_count, tip_group)):
		#print t, cat, triple_count[t]
		print "%s\t%s" %(cat, "\t".join((str(c) for c in triple_count[t])))

