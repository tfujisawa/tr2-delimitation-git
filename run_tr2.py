#! /usr/bin/env python

import sys
import types
import argparse

from tr2.likmodel import *
from tr2.triple_utils import *
from tr2.guidesearch import *
from tr2.rt_consensus import *

def parse_arguments(args):
	parse = argparse.ArgumentParser(description="Multilocus species delimitation using trinomial distribution of triplets")
	parse.add_argument("-t", metavar="gene_trees", required=True, help="gene trees of loci in Newick")
	parse.add_argument("-g", metavar="guide_tree", required=False, help="a guide tree in Newick")
	parse.add_argument("-a", metavar="association", required=False, help="delimitation hypothesis in tab delimited txt")
	#parse.add_argument("-N", metavar="#tree", required=False, help="number of gene trees used in analysis")
	parse.add_argument("-o", metavar="output prefix", required=False, help="prefix for output files")

	parse.add_argument("-C", required=False, action="store_true")

	return parse.parse_args(args[1:])


def model_comparison(treefile, assocfile, N="ALL"):
	#if treefile is string, open a file, else directly pass to "count_triple" function
	if type(treefile) is types.StringType:	
		with open(treefile, "r") as f:
			triple_count = count_triples(f, num_tree=N)	
	else:
		triple_count = count_triples(treefile, num_tree=N)

	groups = []
	with open(assocfile) as f:
		for line in f:
			if not line.startswith("#"):
				l = line.rstrip("\n").split("\t")
				groups.append(tuple(l))

	N = len(groups[0]) - 1

	#nullik = NullLikelihood()
	#mixlik = MixedLikelihood()

	ppmodel = ModelPosterior()

	L = len(triple_count)
	nullscore = ppmodel.calculate(triple_count.values(), ["NULL"]*L)
	#nullscore = nullik.calculate(triple_count.values())

	mixscores = []
	for i in range(N):
		tip_group = {}
		for g in groups:
			tip_group[g[0]] = g[i+1]

		print tip_group

		mixscores.append(ppmodel.calculate(triple_count.values(), categorize_triples(triple_count, tip_group)))

	#print nullscore
	#print mixscores

	return [nullscore] + mixscores


def search(treefile, guidefile, stype="r", N="ALL"):
	if type(treefile) is types.StringType:	
		with open(treefile, "r") as f:
			triple_count = count_triples(f, num_tree=N)	
	else:
		triple_count = count_triples(treefile, num_tree=N)

	with open(guidefile, "r") as f:
		for i, line in enumerate(f):
			if i > 1:
				print "There are multiple trees in input guide tree file, %s" % sys.arv[2]
				print "First tree is used."
				break	
			gtree = GuideTree(parse_newick(line.rstrip("\n")))

	if stype == "g":	#greedy search
		restree = greedy_search(triple_count, gtree)
		#print restree.list_species()

	elif stype == "r":	#recursive search
		restree = recursive_search_D(triple_count, gtree)

	for nod in restree.species_nodes + restree.species_tips:
		if nod.label:
			nod.label = "*" + nod.label
		else:
			nod.label = "*"

	return restree

def build_consensus(treefile):
	#count number of taxa
	num_taxa = []
	with open(treefile, "r") as f:
		for line in f:
			tr = parse_newick(line.rstrip("\n"))
			num_taxa.append(len(tr.name))

	ave_taxa = sum(num_taxa)/len(num_taxa)

	#running triplec
	print "building rooted triple consensus with %d iterations..." % (50*ave_taxa)

	bindir = os.path.dirname(sys.argv[0]) + "/bin"
	if os.path.exists(bindir+"/Triplec.jar"):
		print "Triplec directory: " + bindir
		rtc = run_triplec(treefile, nrep=50*ave_taxa, bindir=bindir)
	else:
		print bindir + "/Triplec.jar does not exist."	
	return rtc

def list_scores(scores):
	text = "model\tscore\n"
	text += "null\t%0.2f\n" % scores[0]
	for i, r in enumerate(scores[1:]):
		text += "model%d\t%0.2f\n" % (i+1, r)

	return text.rstrip("\n")

if __name__=="__main__":
	args = parse_arguments(sys.argv)

	if args.o:
		out_table = open(args.o+".table.txt", "w")
		out_tree = open(args.o+".tre", "w")
	else:
		out_table = sys.stdout
		out_tree = sys.stdout

	if args.g:
		print "run guide search"
		print args.t
		print args.g
	
		res = search(args.t, args.g)
		print "write: %s" % out_tree.name
		print >> out_tree, res
		print "write: %s" % out_table.name
		print >> out_table, create_table(res)
	else:
		if args.a:
			print "run model comparison"
			print args.t			
			print args.a

			res = model_comparison(args.t, args.a)
			print "write: %s" % out_table.name
			print >> out_table, list_scores(res)		
			
		else:
			print "run tree search + guide search"
			print args.t
			
			ctr = build_consensus(args.t)
			
			with open(args.t+"_rtc", "w") as f:
				f.write(ctr)
			
			if args.C:
				print "quite program after consensus tree building (-C option)"
				sys.exit(0)

			res = search(args.t, args.t+"_rtc")

			print "write: %s" % out_tree.name	
			print >> out_tree, res
			print "write: %s" % out_table.name
			print >> out_table, create_table(res)


		
